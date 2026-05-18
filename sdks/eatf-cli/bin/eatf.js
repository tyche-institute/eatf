#!/usr/bin/env node
// @eatf/cli — `eatf agents sync <manifest.yaml>`
//
// Minimal-surface CLI for the EATF agent registry. One command for now:
// `agents sync <file>`. Reads `EATF_API_KEY` (required) and `EATF_BASE_URL`
// (optional, defaults to https://api.eatf.eu) from the environment.
//
// Designed to be a one-line drop-in for partner CI:
//
//   - run: npx -y @eatf/cli@latest agents sync ./agent.yaml
//     env:
//       EATF_API_KEY: ${{ secrets.EATF_API_KEY }}
//
// Exit codes:
//   0 — created or updated
//   1 — conflict (agentId taken by a different tenant) or HTTP error
//   2 — invalid arguments or unreadable / invalid manifest
//
// All flags are positional + env. Add subcommands here as RFC #72 expands.

import process from "node:process";
import { randomUUID } from "node:crypto";
import { writeFile, access, readFile } from "node:fs/promises";
import path from "node:path";
import {
  readManifest,
  syncAgent,
  attestAction,
  listAgents,
  getAgent,
  signResponse,
  downloadEvidence,
  verifyEvidence,
  probeBackend,
  EVIDENCE_BUNDLE_FILES,
  ManifestError,
} from "../src/lib.js";

const HELP = `eatf — EATF agent registry CLI

USAGE
  eatf init <slug> [--out <path>]    scaffold a fresh agent.yaml
  eatf agents sync <manifest.yaml>   PUT a manifest to the registry
  eatf list [--json]                 list agents on the API key's tenant
  eatf get <agent-id|--manifest p>   fetch one agent by id (or from manifest)
  eatf attest                        POST an action attestation
      --agent-id <urn> | --manifest <path>
      --action <type>
      --input  <text> | --input-file  <path>
      --output <text> | --output-file <path>
      [--policy-id atap-basic] [--policy-version 1.0]
  eatf sign                          POST /api/sign + optional .aep download
      --response <text> | --response-file <path>
      [--prompt <text> | --prompt-file <path>]
      [--model-id external] [--policy-id atap-basic] [--policy-version 1.0]
      [--download <path>]                # write .aep to <path>
  eatf verify <evidence.aep>         offline structural + crypto verify
                                       (no network, no API key needed)
  eatf doctor [--manifest <path>]    end-to-end diagnostic (env, net, auth,
                                       tenant, manifest, agent, attest)

ENV
  EATF_API_KEY    long-lived bearer token (alth_live_...). Required for sync/attest.
  EATF_BASE_URL   EATF backend base URL. Default: https://api.eatf.eu

EXIT CODES
  0  success (file written, HTTP 200/201, or attestation accepted)
  1  cross-tenant conflict (HTTP 409) or other HTTP failure
  2  invalid arguments, invalid / unreadable manifest, refused overwrite

See the manifest format in sdks/eatf-cli/README.md or the AEP profile v1 spec.
`;

function printHelp(stream = process.stdout) {
  stream.write(HELP);
}

function die(code, message) {
  process.stderr.write(message.endsWith("\n") ? message : message + "\n");
  process.exit(code);
}

function parseArgv(argv) {
  // argv = [...rest of process.argv after `node bin/eatf.js`]
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    return { kind: "help" };
  }
  if (argv.includes("--version") || argv.includes("-V")) {
    return { kind: "version" };
  }
  const [command, sub, ...rest] = argv;
  if (command === "agents" && sub === "sync") {
    if (rest.length !== 1) {
      return { kind: "error", message: "usage: eatf agents sync <manifest.yaml>" };
    }
    return { kind: "agents-sync", file: rest[0] };
  }
  if (command === "init") {
    if (sub === undefined || sub.startsWith("-")) {
      return { kind: "error", message: "usage: eatf init <slug> [--out <path>]" };
    }
    let out = "agent.yaml";
    for (let i = 0; i < rest.length; i++) {
      if (rest[i] === "--out" || rest[i] === "-o") {
        if (rest[i + 1] === undefined) {
          return { kind: "error", message: "--out requires a path argument" };
        }
        out = rest[i + 1];
        i++;
      } else {
        return { kind: "error", message: `unknown init flag: ${rest[i]}` };
      }
    }
    return { kind: "init", slug: sub, out };
  }
  if (command === "list") {
    const flags = sub === undefined ? [] : [sub, ...rest];
    let json = false;
    for (let i = 0; i < flags.length; i++) {
      if (flags[i] === "--json") { json = true; continue; }
      return { kind: "error", message: `unknown list flag: ${flags[i]}` };
    }
    return { kind: "list", json };
  }
  if (command === "get") {
    const flags = sub === undefined ? [] : [sub, ...rest];
    let agentId = null;
    let manifest = null;
    let json = false;
    for (let i = 0; i < flags.length; i++) {
      const f = flags[i];
      if (f === "--manifest") {
        if (flags[i + 1] === undefined) return { kind: "error", message: "--manifest requires a path" };
        manifest = flags[++i];
      } else if (f === "--json") {
        json = true;
      } else if (!f.startsWith("-")) {
        if (agentId !== null) return { kind: "error", message: "get: pass exactly one agent id (or --manifest)" };
        agentId = f;
      } else {
        return { kind: "error", message: `unknown get flag: ${f}` };
      }
    }
    if (!agentId && !manifest) {
      return { kind: "error", message: "usage: eatf get <agent-id> | --manifest <path>" };
    }
    if (agentId && manifest) {
      return { kind: "error", message: "get: pass either an agent id or --manifest, not both" };
    }
    return { kind: "get", agentId, manifest, json };
  }
  if (command === "doctor") {
    const flags = sub === undefined ? [] : [sub, ...rest];
    let manifest = null;
    for (let i = 0; i < flags.length; i++) {
      if (flags[i] === "--manifest") {
        if (flags[i + 1] === undefined) {
          return { kind: "error", message: "--manifest requires a path" };
        }
        manifest = flags[++i];
      } else {
        return { kind: "error", message: `unknown doctor flag: ${flags[i]}` };
      }
    }
    return { kind: "doctor", manifest };
  }
  if (command === "verify") {
    if (sub === undefined) {
      return { kind: "error", message: "usage: eatf verify <evidence.aep>" };
    }
    if (rest.length > 0) {
      return { kind: "error", message: `unknown verify args: ${rest.join(" ")}` };
    }
    return { kind: "verify", file: sub };
  }
  if (command === "sign") {
    const flags = sub === undefined ? [] : [sub, ...rest];
    const opts = {
      prompt: null, promptFile: null,
      response: null, responseFile: null,
      modelId: null, policyId: null, policyVersion: null,
      download: null,
    };
    for (let i = 0; i < flags.length; i++) {
      const f = flags[i];
      const need = (k) => {
        if (flags[i + 1] === undefined) throw new Error(`${k} requires a value`);
        i++;
        return flags[i];
      };
      try {
        switch (f) {
          case "--prompt":         opts.prompt         = need("--prompt");         break;
          case "--prompt-file":    opts.promptFile     = need("--prompt-file");    break;
          case "--response":       opts.response       = need("--response");       break;
          case "--response-file":  opts.responseFile   = need("--response-file");  break;
          case "--model-id":       opts.modelId        = need("--model-id");       break;
          case "--policy-id":      opts.policyId       = need("--policy-id");      break;
          case "--policy-version": opts.policyVersion  = need("--policy-version"); break;
          case "--download":       opts.download       = need("--download");       break;
          default:
            return { kind: "error", message: `unknown sign flag: ${f}` };
        }
      } catch (e) {
        return { kind: "error", message: e.message };
      }
    }
    if ((opts.response == null) === (opts.responseFile == null)) {
      return { kind: "error", message: "sign: exactly one of --response or --response-file is required" };
    }
    if (opts.prompt != null && opts.promptFile != null) {
      return { kind: "error", message: "sign: pass at most one of --prompt or --prompt-file" };
    }
    return { kind: "sign", opts };
  }
  if (command === "attest") {
    // attest takes no positional; everything is via --flag value pairs.
    const flags = sub === undefined ? [] : [sub, ...rest];
    const opts = {
      agentId: null,
      manifest: null,
      action: null,
      input: null,
      inputFile: null,
      output: null,
      outputFile: null,
      policyId: null,
      policyVersion: null,
    };
    for (let i = 0; i < flags.length; i++) {
      const need = (k) => {
        if (flags[i + 1] === undefined) {
          throw new Error(`${k} requires a value argument`);
        }
        i++;
        return flags[i];
      };
      try {
        switch (flags[i]) {
          case "--agent-id":       opts.agentId       = need("--agent-id");       break;
          case "--manifest":       opts.manifest      = need("--manifest");       break;
          case "--action":         opts.action        = need("--action");         break;
          case "--input":          opts.input         = need("--input");          break;
          case "--input-file":     opts.inputFile     = need("--input-file");     break;
          case "--output":         opts.output        = need("--output");         break;
          case "--output-file":    opts.outputFile    = need("--output-file");    break;
          case "--policy-id":      opts.policyId      = need("--policy-id");      break;
          case "--policy-version": opts.policyVersion = need("--policy-version"); break;
          default:
            return { kind: "error", message: `unknown attest flag: ${flags[i]}` };
        }
      } catch (e) {
        return { kind: "error", message: e.message };
      }
    }
    if (!opts.agentId && !opts.manifest) {
      return { kind: "error", message: "attest: --agent-id <urn> OR --manifest <path> is required" };
    }
    if (opts.agentId && opts.manifest) {
      return { kind: "error", message: "attest: pass either --agent-id or --manifest, not both" };
    }
    if (!opts.action) {
      return { kind: "error", message: "attest: --action <type> is required" };
    }
    if ((opts.input == null) === (opts.inputFile == null)) {
      return { kind: "error", message: "attest: exactly one of --input or --input-file is required" };
    }
    if ((opts.output == null) === (opts.outputFile == null)) {
      return { kind: "error", message: "attest: exactly one of --output or --output-file is required" };
    }
    return { kind: "attest", opts };
  }
  return { kind: "error", message: `unknown command: ${argv.join(" ")}\n\n${HELP}` };
}

async function readPackageVersion() {
  // Resolve package.json relative to this script. Works when invoked via npx,
  // a global install, or from a checkout.
  try {
    const url = new URL("../package.json", import.meta.url);
    const text = await (await import("node:fs/promises")).readFile(url, "utf8");
    return JSON.parse(text).version;
  } catch {
    return "unknown";
  }
}

function renderResult(result) {
  const arrow = result.outcome === "created" ? "+" : result.outcome === "updated" ? "~" : "!";
  const tag = result.outcome.toUpperCase();
  const head = `[${arrow}] ${tag} ${result.agentId} (${result.status} ${result.baseUrl})`;
  const detail =
    result.outcome === "created" || result.outcome === "updated"
      ? `    name=${result.body?.name ?? "?"} tenantId=${result.body?.tenantId ?? "?"} eidasCertificate=${result.body?.eidasCertificateArn ?? "(none)"}`
      : `    ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}`;
  return `${head}\n${detail}\n`;
}

function manifestTemplate({ slug, agentId }) {
  // Keep this in sync with sdks/eatf-cli/README.md and the sample manifest at
  // partner-integrations/eu-ai-act-agent/agent.yaml. Comments describe each
  // field in plain English so a YAML newcomer doesn't need to open the docs.
  return `# Generated by \`eatf init ${slug}\` on ${new Date().toISOString().slice(0, 10)}.
# Edit the values below, then sync with:
#
#   EATF_API_KEY=alth_live_... npx -y @eatf/cli@latest agents sync ${path.basename("agent.yaml")}
#
# The first sync creates the agent on the API key's tenant; subsequent syncs
# patch mutable fields in place. Cross-tenant slug collisions return 409.

# Stable identifier. Caller-picked, used forever. \`urn:uuid:\` is recommended
# (zero collision risk); a namespaced slug like \`acme:fraud-detector\` works
# too as long as you keep it unique across tenants.
agentId: ${agentId}

# Human-readable name (≤ 255 chars).
displayName: ${slug}

# One-line description; surfaced in the EATF UI and the evidence package.
description: "TODO: describe what ${slug} does"

# Type taxonomy: custom | conversational | analytical | autonomous | robotic | ...
agentType: custom

# Risk tier: minimal | limited | high. \`high\` triggers the EU AI Act
# Article 6 trust architecture (qualified eIDAS, Article 14 review queues).
riskClassification: limited

# Capabilities surfaced in the registry; freeform tags.
capabilities:
  - TODO

# Optional: eIDAS level (simple | advanced | qualified) and a pre-existing
# certificate ARN. Leave blank to let the registry issue one on first sync.
# eidasLevel: simple
# eidasCertificateArn: pki:cert:...

# Optional: signing algorithm preference (HYBRID | RSA | ML-DSA).
# signatureAlgorithm: HYBRID

# Optional: jurisdiction tag.
# primaryJurisdiction: EU

# Optional: organization / contact for the public registry view.
# organization: Acme Corp
# contactEmail: ops@acme.example
`;
}

async function runInit(slug, out) {
  if (!/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(slug)) {
    die(
      2,
      `init: slug "${slug}" is not a friendly identifier; expected ` +
        `[a-zA-Z0-9][a-zA-Z0-9._-]*. Pick something readable; the agentId in ` +
        `the YAML defaults to a urn:uuid: regardless.`,
    );
  }
  const target = path.resolve(out);
  try {
    await access(target);
    die(2, `init: ${target} already exists; refusing to overwrite. Use --out <path> or remove the file first.`);
  } catch {
    // ENOENT — good.
  }
  const agentId = `urn:uuid:${randomUUID()}`;
  const content = manifestTemplate({ slug, agentId });
  await writeFile(target, content, { encoding: "utf8" });
  process.stdout.write(
    `[+] wrote ${target}\n` +
      `    agentId: ${agentId}\n` +
      `    displayName: ${slug}\n\n` +
      `Next:\n` +
      `  1. Edit ${path.basename(target)} (capabilities, riskClassification, eidasLevel).\n` +
      `  2. Mint an API key in the EATF UI on the right tenant; copy alth_live_...\n` +
      `  3. EATF_API_KEY=alth_live_... npx -y @eatf/cli@latest agents sync ${path.basename(target)}\n`,
  );
  return 0;
}

function pad(s, w) {
  s = String(s ?? "");
  return s.length >= w ? s : s + " ".repeat(w - s.length);
}

function renderAgentTable(agents) {
  if (agents.length === 0) {
    return "(no agents on this tenant — try `eatf init <slug>` then `eatf agents sync agent.yaml`)\n";
  }
  // Compute column widths capped to keep terminal-friendly.
  const cap = (n, max) => Math.min(Math.max(n, 1), max);
  const idW   = cap(Math.max(...agents.map((a) => (a.agentId ?? "").length)), 60);
  const nameW = cap(Math.max(...agents.map((a) => (a.name ?? "").length)), 30);
  const typeW = cap(Math.max(...agents.map((a) => (a.agentType ?? "").length)), 14);
  const riskW = cap(Math.max(...agents.map((a) => (a.riskClassification ?? "").length)), 8);
  const lines = [
    `${pad("AGENT_ID", idW)}  ${pad("NAME", nameW)}  ${pad("TYPE", typeW)}  ${pad("RISK", riskW)}  STATUS`,
  ];
  for (const a of agents) {
    lines.push(
      `${pad((a.agentId ?? "").slice(0, idW), idW)}  ${pad((a.name ?? "").slice(0, nameW), nameW)}  ${pad((a.agentType ?? "").slice(0, typeW), typeW)}  ${pad((a.riskClassification ?? "").slice(0, riskW), riskW)}  ${a.status ?? "?"}`,
    );
  }
  return lines.join("\n") + "\n";
}

async function runList(json) {
  const apiKey = process.env.EATF_API_KEY;
  if (!apiKey) {
    die(2, "EATF_API_KEY is required (export EATF_API_KEY=alth_live_...)");
  }
  const baseUrl = process.env.EATF_BASE_URL;
  const result = await listAgents({ apiKey, baseUrl });
  if (result.outcome !== "ok") {
    process.stderr.write(
      `[!] ERROR list (${result.status} ${result.baseUrl})\n` +
        `    ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}\n`,
    );
    return 1;
  }
  if (json) {
    process.stdout.write(JSON.stringify(result.agents, null, 2) + "\n");
    return 0;
  }
  process.stdout.write(`[#] ${result.agents.length} agent(s) on this tenant (${result.baseUrl})\n`);
  process.stdout.write(renderAgentTable(result.agents));
  return 0;
}

async function runGet({ agentId, manifest, json }) {
  const apiKey = process.env.EATF_API_KEY;
  if (!apiKey) {
    die(2, "EATF_API_KEY is required (export EATF_API_KEY=alth_live_...)");
  }
  const baseUrl = process.env.EATF_BASE_URL;

  let resolvedId = agentId;
  if (!resolvedId) {
    try {
      const m = await readManifest(manifest);
      resolvedId = m.agentId;
    } catch (err) {
      if (err instanceof ManifestError) die(2, `manifest error: ${err.message}`);
      throw err;
    }
  }

  const result = await getAgent({ agentId: resolvedId, apiKey, baseUrl });
  if (result.outcome === "not-found") {
    process.stderr.write(
      `[?] NOT FOUND ${resolvedId} (404 ${result.baseUrl})\n` +
        `    Either the manifest hasn't been synced yet (run \`eatf agents sync\`)\n` +
        `    or the agent belongs to a different tenant — pick the right API key.\n`,
    );
    return 1;
  }
  if (result.outcome !== "ok") {
    process.stderr.write(
      `[!] ERROR ${resolvedId} (${result.status} ${result.baseUrl})\n` +
        `    ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}\n`,
    );
    return 1;
  }
  if (json) {
    process.stdout.write(JSON.stringify(result.agent, null, 2) + "\n");
    return 0;
  }
  const a = result.agent;
  process.stdout.write(
    `[+] ${a.agentId} (${result.status} ${result.baseUrl})\n` +
      `    name=${a.name ?? "?"}\n` +
      `    type=${a.agentType ?? "?"}  risk=${a.riskClassification ?? "?"}  status=${a.status ?? "?"}\n` +
      `    eidasLevel=${a.eidasLevel ?? "(none)"}  eidasCertificate=${a.eidasCertificateArn ?? "(none)"}\n` +
      `    organization=${a.organization ?? "(none)"}\n` +
      `    registeredAt=${a.registeredAt ?? "?"}\n` +
      `    updatedAt=${a.updatedAt ?? "?"}\n`,
  );
  return 0;
}

// Symbols for the doctor checklist. Plain ASCII so the output stays readable
// in CI logs that strip ANSI / Unicode.
const DOC_PASS = "[+]";
const DOC_FAIL = "[!]";
const DOC_WARN = "[?]";
const DOC_SKIP = "[-]";

function maskKey(key) {
  if (typeof key !== "string" || key.length < 12) return "(too short)";
  return `${key.slice(0, 12)}***${key.slice(-4)}`;
}

async function runDoctor({ manifest: manifestPath }) {
  const lines = [];
  let failed = 0;

  // 1. ENV
  const apiKey = process.env.EATF_API_KEY;
  const baseUrl = process.env.EATF_BASE_URL || "https://api.eatf.eu";
  if (apiKey) {
    lines.push(`${DOC_PASS} ENV       EATF_API_KEY set (${maskKey(apiKey)})`);
  } else {
    lines.push(`${DOC_FAIL} ENV       EATF_API_KEY is not set`);
    lines.push(`           export EATF_API_KEY=alth_live_...`);
    failed++;
  }
  lines.push(`${DOC_PASS} ENV       EATF_BASE_URL=${baseUrl}${process.env.EATF_BASE_URL ? "" : " (default)"}`);

  // 2. NET
  const probe = await probeBackend({ baseUrl });
  if (probe.outcome === "reachable") {
    lines.push(`${DOC_PASS} NET       ${baseUrl} reachable (${probe.status}, ${probe.latencyMs}ms)`);
  } else {
    lines.push(`${DOC_FAIL} NET       ${baseUrl} not reachable: ${probe.error ?? `HTTP ${probe.status}`}`);
    lines.push(`           Check EATF_BASE_URL or your egress (Caddy host-allowlist may block GH-runner egress)`);
    failed++;
  }

  // Stop here if we have no apiKey or backend is down — further checks would
  // all fail with the same root cause and just add noise.
  if (!apiKey || probe.outcome !== "reachable") {
    return renderDoctor(lines, failed);
  }

  // 3. AUTH + 4. TENANT
  const list = await listAgents({ apiKey, baseUrl });
  if (list.outcome === "ok") {
    lines.push(`${DOC_PASS} AUTH      key authenticates`);
    const sample = list.agents.slice(0, 5).map((a) => a.agentId).join(", ");
    lines.push(`${DOC_PASS} TENANT    ${list.agents.length} agent(s) on this tenant${sample ? ` — ${sample}${list.agents.length > 5 ? ", …" : ""}` : ""}`);
  } else if (list.status === 401) {
    lines.push(`${DOC_FAIL} AUTH      HTTP 401 — API key rejected`);
    lines.push(`           Mint a fresh key in the EATF UI and update EATF_API_KEY`);
    failed++;
    return renderDoctor(lines, failed);
  } else {
    lines.push(`${DOC_FAIL} AUTH      HTTP ${list.status} from /api/v1/agents`);
    lines.push(`           ${typeof list.body === "string" ? list.body : JSON.stringify(list.body)}`);
    failed++;
    return renderDoctor(lines, failed);
  }

  if (!manifestPath) {
    lines.push(`${DOC_SKIP} MANIFEST  (skipped — pass --manifest <path> to also check the manifest)`);
    return renderDoctor(lines, failed);
  }

  // 5. MANIFEST
  let manifest;
  try {
    manifest = await readManifest(manifestPath);
    lines.push(`${DOC_PASS} MANIFEST  ${manifestPath} parses; agentId=${manifest.agentId}`);
  } catch (err) {
    lines.push(`${DOC_FAIL} MANIFEST  ${err instanceof ManifestError ? err.message : err.message}`);
    failed++;
    return renderDoctor(lines, failed);
  }

  // 6. AGENT — is the manifest's agentId on the caller's tenant?
  const got = await getAgent({ agentId: manifest.agentId, apiKey, baseUrl });
  if (got.outcome === "ok") {
    const a = got.agent;
    lines.push(
      `${DOC_PASS} AGENT     registered on this tenant; status=${a.status ?? "?"}, risk=${a.riskClassification ?? "?"}, eidasLevel=${a.eidasLevel ?? "(none)"}`,
    );
  } else if (got.outcome === "not-found") {
    lines.push(`${DOC_WARN} AGENT     not registered yet — run \`eatf agents sync ${manifestPath}\``);
    lines.push(`${DOC_SKIP} ATTEST    (skipped — agent must exist before attesting)`);
    return renderDoctor(lines, failed); // not a hard failure; expected during onboarding
  } else {
    lines.push(`${DOC_FAIL} AGENT     HTTP ${got.status} from /api/v1/agents/${manifest.agentId}`);
    failed++;
    return renderDoctor(lines, failed);
  }

  // 7. ATTEST smoke
  const attest = await attestAction({
    agentId: manifest.agentId,
    actionType: "DOCTOR_SMOKE",
    input: "eatf doctor smoke",
    output: "ok",
    apiKey,
    baseUrl,
  });
  if (attest.outcome === "attested") {
    lines.push(`${DOC_PASS} ATTEST    smoke attestation accepted (attestationId=${attest.attestationId})`);
  } else {
    lines.push(`${DOC_FAIL} ATTEST    HTTP ${attest.status}: ${typeof attest.body === "string" ? attest.body : JSON.stringify(attest.body)}`);
    failed++;
  }

  return renderDoctor(lines, failed);
}

function renderDoctor(lines, failed) {
  for (const l of lines) process.stdout.write(l + "\n");
  process.stdout.write(
    failed === 0
      ? `\nAll checks passed.\n`
      : `\n${failed} check(s) failed.\n`,
  );
  return failed === 0 ? 0 : 1;
}

async function runVerify(file) {
  let result;
  try {
    result = await verifyEvidence({ path: file });
  } catch (err) {
    process.stderr.write(`[!] cannot read ${file}: ${err.message}\n`);
    return 2;
  }
  if (result.outcome === "valid") {
    const meta = result.metadata ?? {};
    const unsigned = result.unsignedSuffixBytes ?? 0;
    let lines =
      `[+] VALID ${result.path}\n` +
      `    response_canonical (${result.responseCanonicalBytes} bytes) hash + signature verify\n` +
      `    sha256=${result.hash}\n` +
      `    signature=${result.signatureBytes} bytes  tsaToken=${result.tsaTokenBytes} bytes\n` +
      `    model=${meta.model ?? meta.modelId ?? "?"}  policyVersion=${meta.policyVersion ?? "?"}  createdAt=${meta.createdAt ?? "?"}\n`;
    if (unsigned > 0) {
      lines +=
        `    note: ${unsigned} bytes of unsigned claim/policy envelope follow the response_canonical prefix.\n` +
        `          Tampering of the envelope is undetectable by hash+signature alone (backend design).\n`;
    }
    lines +=
      `    note: TSA chain not verified — run aletheia-verifier.jar for full RFC 3161 validation\n`;
    process.stdout.write(lines);
    return 0;
  }
  switch (result.outcome) {
    case "missing-files":
      process.stderr.write(
        `[!] INVALID ${result.path}\n` +
          `    missing: ${result.missing.join(", ")}\n` +
          `    expected: ${EVIDENCE_BUNDLE_FILES.join(", ")}\n`,
      );
      break;
    case "hash-mismatch":
      process.stderr.write(
        `[!] INVALID ${result.path} — hash mismatch (response was tampered with)\n` +
          `    expected ${result.expectedHash}\n` +
          `    computed ${result.computedHash}\n`,
      );
      break;
    case "signature-invalid":
      process.stderr.write(
        `[!] INVALID ${result.path} — signature does not verify\n` +
          (result.error ? `    ${result.error}\n` : "") +
          `    hash=${result.hash}\n`,
      );
      break;
    case "tsa-empty":
      process.stderr.write(
        `[!] INVALID ${result.path} — timestamp.tsr is empty\n`,
      );
      break;
    case "metadata-invalid":
      process.stderr.write(
        `[!] INVALID ${result.path} — metadata.json is not parseable JSON\n` +
          (result.error ? `    ${result.error}\n` : ""),
      );
      break;
    case "zip-invalid":
      process.stderr.write(
        `[!] INVALID ${result.path} — not a parseable zip\n` +
          (result.error ? `    ${result.error}\n` : ""),
      );
      break;
    default:
      process.stderr.write(`[!] INVALID ${result.path} — ${result.outcome}\n`);
  }
  return 1;
}

async function runSign(opts) {
  const apiKey = process.env.EATF_API_KEY;
  if (!apiKey) {
    die(2, "EATF_API_KEY is required (export EATF_API_KEY=alth_live_...)");
  }
  const baseUrl = process.env.EATF_BASE_URL;

  const readArg = async (label, inline, file) => {
    if (inline != null) return inline;
    if (file == null) return undefined;
    try {
      return await readFile(file, "utf8");
    } catch (err) {
      die(2, `${label}: cannot read ${file}: ${err.message}`);
      return "";
    }
  };
  const response = await readArg("--response-file", opts.response, opts.responseFile);
  const prompt   = await readArg("--prompt-file",   opts.prompt,   opts.promptFile);

  const result = await signResponse({
    response,
    prompt,
    modelId: opts.modelId ?? undefined,
    policyId: opts.policyId ?? undefined,
    policyVersion: opts.policyVersion ?? undefined,
    apiKey,
    baseUrl,
  });
  if (result.outcome !== "signed") {
    process.stderr.write(
      `[!] ERROR sign (${result.status} ${result.baseUrl})\n` +
        `    ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}\n`,
    );
    return 1;
  }
  process.stdout.write(
    `[+] SIGNED (${result.status} ${result.baseUrl})\n` +
      `    stampId=${result.stampId}\n` +
      `    uuid=${result.uuid ?? "?"}\n` +
      `    responseHash=${result.responseHash ?? "?"}\n` +
      `    tsaToken=${result.tsaToken ? "present" : "(missing — TSA disabled?)"}\n` +
      `    evidenceUrl=${result.evidenceUrl}\n`,
  );

  if (opts.download) {
    const dl = await downloadEvidence({
      stampId: result.stampId,
      outPath: opts.download,
      apiKey,
      baseUrl,
    });
    if (dl.outcome !== "downloaded") {
      process.stderr.write(
        `[!] WARN evidence download failed (${dl.status} ${dl.baseUrl})\n` +
          `    Sign succeeded; the bundle is still retrievable at ${result.evidenceUrl}\n`,
      );
      return 1;
    }
    process.stdout.write(
      `[+] DOWNLOADED ${dl.path} (${dl.size.toLocaleString("en-US")} bytes)\n`,
    );
  }
  return 0;
}

function renderAttestResult(result) {
  if (result.outcome === "attested") {
    const lines = [
      `[+] ATTESTED ${result.agentId} (${result.status} ${result.baseUrl})`,
      `    attestationId=${result.attestationId ?? "?"}`,
    ];
    if (result.body && typeof result.body === "object" && result.body.canonicalHash) {
      lines.push(`    canonicalHash=${result.body.canonicalHash}`);
    }
    return lines.join("\n") + "\n";
  }
  return (
    `[!] ERROR ${result.agentId} (${result.status} ${result.baseUrl})\n` +
    `    ${typeof result.body === "string" ? result.body : JSON.stringify(result.body)}\n`
  );
}

async function runAttest(opts) {
  const apiKey = process.env.EATF_API_KEY;
  if (!apiKey) {
    die(2, "EATF_API_KEY is required (export EATF_API_KEY=alth_live_...)");
  }
  const baseUrl = process.env.EATF_BASE_URL;

  // Resolve agent id from --agent-id or --manifest.
  let agentId = opts.agentId;
  if (!agentId) {
    try {
      const manifest = await readManifest(opts.manifest);
      agentId = manifest.agentId;
    } catch (err) {
      if (err instanceof ManifestError) die(2, `manifest error: ${err.message}`);
      throw err;
    }
  }

  // Resolve input/output from inline flags or files.
  const readArg = async (label, inline, file) => {
    if (inline != null) return inline;
    try {
      return await readFile(file, "utf8");
    } catch (err) {
      die(2, `${label}: cannot read ${file}: ${err.message}`);
      return ""; // unreachable; satisfies TS-style flow
    }
  };
  const input = await readArg("--input-file", opts.input, opts.inputFile);
  const output = await readArg("--output-file", opts.output, opts.outputFile);

  const result = await attestAction({
    agentId,
    actionType: opts.action,
    input,
    output,
    policyId: opts.policyId ?? undefined,
    policyVersion: opts.policyVersion ?? undefined,
    baseUrl,
    apiKey,
  });
  process.stdout.write(renderAttestResult(result));
  return result.outcome === "attested" ? 0 : 1;
}

async function runAgentsSync(file) {
  const apiKey = process.env.EATF_API_KEY;
  if (!apiKey) {
    die(2, "EATF_API_KEY is required (export EATF_API_KEY=alth_live_...)");
  }
  const baseUrl = process.env.EATF_BASE_URL;

  let manifest;
  try {
    manifest = await readManifest(file);
  } catch (err) {
    if (err instanceof ManifestError) die(2, `manifest error: ${err.message}`);
    throw err;
  }

  const result = await syncAgent({ manifest, baseUrl, apiKey });
  process.stdout.write(renderResult(result));

  if (result.outcome === "created" || result.outcome === "updated") return 0;
  if (result.outcome === "conflict") return 1;
  return 1;
}

async function main() {
  const argv = process.argv.slice(2);
  const parsed = parseArgv(argv);

  switch (parsed.kind) {
    case "help":
      printHelp();
      return 0;
    case "version": {
      const version = await readPackageVersion();
      process.stdout.write(`@eatf/cli ${version}\n`);
      return 0;
    }
    case "error":
      die(2, parsed.message);
      return 2;
    case "init":
      return await runInit(parsed.slug, parsed.out);
    case "list":
      return await runList(parsed.json);
    case "get":
      return await runGet(parsed);
    case "sign":
      return await runSign(parsed.opts);
    case "verify":
      return await runVerify(parsed.file);
    case "doctor":
      return await runDoctor(parsed);
    case "attest":
      return await runAttest(parsed.opts);
    case "agents-sync":
      return await runAgentsSync(parsed.file);
    default:
      die(2, "internal: unhandled command kind");
      return 2;
  }
}

main().then(
  (code) => process.exit(code),
  (err) => {
    process.stderr.write(`unexpected error: ${err?.stack ?? err}\n`);
    process.exit(1);
  },
);
