// Tests for @eatf/cli internals. Run with `node --test`.
//
// Covers: manifest validation, manifest-to-body translation, and the
// outcome mapping in `syncAgent` against an in-memory fetch stub.
// HTTP-against-real-backend is a manual smoke test in the README.

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

import crypto from "node:crypto";
import AdmZip from "adm-zip";
import {
  readManifest,
  validateManifest,
  manifestToBody,
  syncAgent,
  attestAction,
  listAgents,
  getAgent,
  signResponse,
  verifyEvidence,
  probeBackend,
  EVIDENCE_BUNDLE_FILES,
  ManifestError,
} from "../src/lib.js";

const SAMPLE = {
  agentId: "eu-ai-act-agent",
  displayName: "EU AI Act Advisor",
  description: "Demo agent for Regulation (EU) 2024/1689",
  agentType: "custom",
  riskClassification: "high",
  capabilities: ["regulatory-qa"],
  eidasLevel: "qualified",
};

async function writeYaml(content) {
  const dir = await mkdtemp(path.join(tmpdir(), "eatf-cli-test-"));
  const file = path.join(dir, "agent.yaml");
  await writeFile(file, content, "utf8");
  return file;
}

test("validateManifest accepts a complete manifest", () => {
  validateManifest(SAMPLE, "<test>");
});

test("validateManifest rejects missing agentId", () => {
  const bad = { ...SAMPLE };
  delete bad.agentId;
  assert.throws(() => validateManifest(bad, "<test>"), ManifestError, /agentId/);
});

test("validateManifest rejects empty displayName", () => {
  assert.throws(() => validateManifest({ ...SAMPLE, displayName: "  " }, "<test>"), ManifestError, /displayName/);
});

test("validateManifest rejects whitespace in agentId", () => {
  assert.throws(() => validateManifest({ ...SAMPLE, agentId: "agent with space" }, "<test>"), ManifestError, /whitespace/);
});

test("validateManifest rejects oversized agentId", () => {
  const tooLong = "x".repeat(256);
  assert.throws(() => validateManifest({ ...SAMPLE, agentId: tooLong }, "<test>"), ManifestError, /255/);
});

test("validateManifest rejects non-array capabilities", () => {
  assert.throws(() => validateManifest({ ...SAMPLE, capabilities: "regulatory-qa" }, "<test>"), ManifestError, /capabilities/);
});

test("manifestToBody maps fields and drops nulls", () => {
  const body = manifestToBody(SAMPLE);
  assert.equal(body.name, "EU AI Act Advisor");
  assert.equal(body.agentType, "custom");
  assert.equal(body.riskClassification, "high");
  assert.deepEqual(body.capabilities, ["regulatory-qa"]);
  assert.equal(body.eidasLevel, "qualified");
  // Optional unset fields should not appear
  assert.equal(Object.prototype.hasOwnProperty.call(body, "transactionLimit"), false);
  assert.equal(Object.prototype.hasOwnProperty.call(body, "mcpDid"), false);
  // agentId belongs in the URL, not the body
  assert.equal(Object.prototype.hasOwnProperty.call(body, "agentId"), false);
});

test("readManifest parses a valid YAML file", async () => {
  const file = await writeYaml(
    "agentId: eu-ai-act-agent\n" +
    "displayName: EU AI Act Advisor\n" +
    "agentType: custom\n" +
    "riskClassification: high\n",
  );
  const manifest = await readManifest(file);
  assert.equal(manifest.agentId, "eu-ai-act-agent");
  assert.equal(manifest.riskClassification, "high");
});

test("readManifest rejects non-mapping YAML", async () => {
  const file = await writeYaml("- just\n- a\n- list\n");
  await assert.rejects(() => readManifest(file), ManifestError, /mapping/);
});

test("readManifest reports the file path on error", async () => {
  const file = await writeYaml("displayName: missing-id\nagentType: custom\nriskClassification: high\n");
  await assert.rejects(
    () => readManifest(file),
    (err) => err instanceof ManifestError && err.path === path.resolve(file),
  );
});

function fakeFetchOk(status, body) {
  return async (_url, _init) => ({
    status,
    text: async () => JSON.stringify(body),
  });
}

test("syncAgent maps 201 → outcome 'created'", async () => {
  const fetchImpl = fakeFetchOk(201, { agentId: "eu-ai-act-agent", name: "EU AI Act Advisor", tenantId: 4 });
  const result = await syncAgent({
    manifest: SAMPLE,
    apiKey: "alth_live_FAKE",
    baseUrl: "https://example.test",
    fetchImpl,
  });
  assert.equal(result.outcome, "created");
  assert.equal(result.status, 201);
  assert.equal(result.agentId, "eu-ai-act-agent");
});

test("syncAgent maps 200 → outcome 'updated'", async () => {
  const fetchImpl = fakeFetchOk(200, { agentId: "eu-ai-act-agent", name: "EU AI Act Advisor", tenantId: 4 });
  const result = await syncAgent({ manifest: SAMPLE, apiKey: "k", fetchImpl });
  assert.equal(result.outcome, "updated");
});

test("syncAgent maps 409 → outcome 'conflict' without leaking owning tenant", async () => {
  const fetchImpl = fakeFetchOk(409, { code: "AGENT_ID_CONFLICT", message: "agentId already in use on a different tenant" });
  const result = await syncAgent({ manifest: SAMPLE, apiKey: "k", fetchImpl });
  assert.equal(result.outcome, "conflict");
  assert.equal(result.body.code, "AGENT_ID_CONFLICT");
  // The CLI should never see a tenant id in the conflict body.
  assert.equal(JSON.stringify(result.body).includes("tenantId"), false);
});

test("syncAgent maps network failure → outcome 'error' (no throw)", async () => {
  const fetchImpl = async () => {
    throw new Error("ECONNREFUSED");
  };
  const result = await syncAgent({ manifest: SAMPLE, apiKey: "k", fetchImpl });
  assert.equal(result.outcome, "error");
  assert.equal(result.status, 0);
  assert.match(result.body.error, /ECONNREFUSED/);
});

test("syncAgent throws on missing apiKey", async () => {
  await assert.rejects(
    () => syncAgent({ manifest: SAMPLE, fetchImpl: fakeFetchOk(200, {}) }),
    /apiKey/,
  );
});

test("syncAgent encodes agentId path component", async () => {
  let observedUrl = null;
  const fetchImpl = async (url) => {
    observedUrl = url;
    return { status: 201, text: async () => "{}" };
  };
  const manifest = { ...SAMPLE, agentId: "eatf-demo:eu-ai-act-agent" };
  await syncAgent({ manifest, apiKey: "k", baseUrl: "https://example.test", fetchImpl });
  assert.equal(observedUrl, "https://example.test/api/v1/agents/eatf-demo%3Aeu-ai-act-agent");
});

test("eatf init generates a valid manifest the validator accepts", async () => {
  // Spawn the bin via a child process so we exercise the same code path
  // partners get via `npx -y @eatf/cli@latest init`.
  const { spawnSync } = await import("node:child_process");
  const dir = await mkdtemp(path.join(tmpdir(), "eatf-cli-init-test-"));
  const bin = new URL("../bin/eatf.js", import.meta.url).pathname;

  const r = spawnSync("node", [bin, "init", "smoke"], { cwd: dir, encoding: "utf8" });
  assert.equal(r.status, 0, `init exited ${r.status}: ${r.stderr}`);
  assert.match(r.stdout, /agentId: urn:uuid:[0-9a-f-]{36}/);
  assert.match(r.stdout, /displayName: smoke/);

  const generated = await readManifest(path.join(dir, "agent.yaml"));
  assert.equal(generated.displayName, "smoke");
  assert.match(generated.agentId, /^urn:uuid:[0-9a-f-]{36}$/);
  assert.equal(generated.agentType, "custom");
  assert.equal(generated.riskClassification, "limited");
  assert.deepEqual(generated.capabilities, ["TODO"]);
});

test("eatf init refuses to overwrite an existing file", async () => {
  const { spawnSync } = await import("node:child_process");
  const dir = await mkdtemp(path.join(tmpdir(), "eatf-cli-init-test-"));
  const bin = new URL("../bin/eatf.js", import.meta.url).pathname;

  const first = spawnSync("node", [bin, "init", "smoke"], { cwd: dir, encoding: "utf8" });
  assert.equal(first.status, 0);

  const second = spawnSync("node", [bin, "init", "smoke"], { cwd: dir, encoding: "utf8" });
  assert.equal(second.status, 2);
  assert.match(second.stderr, /refusing to overwrite/);
});

test("eatf init rejects unfriendly slug", async () => {
  const { spawnSync } = await import("node:child_process");
  const dir = await mkdtemp(path.join(tmpdir(), "eatf-cli-init-test-"));
  const bin = new URL("../bin/eatf.js", import.meta.url).pathname;

  const r = spawnSync("node", [bin, "init", "bad slug with spaces"], { cwd: dir, encoding: "utf8" });
  assert.equal(r.status, 2);
  assert.match(r.stderr, /not a friendly identifier/);
});

// ─── attestAction ────────────────────────────────────────────────────

test("attestAction returns outcome 'attested' on 201", async () => {
  let observed = null;
  const fetchImpl = async (url, init) => {
    observed = { url, init };
    return {
      status: 201,
      text: async () =>
        JSON.stringify({
          attestationId: "att_2026-04-27T12_xyz",
          id: 42,
          policyEvaluation: {},
        }),
    };
  };
  const result = await attestAction({
    agentId: "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
    actionType: "MY_ACTION",
    input: "hello",
    output: "world",
    apiKey: "alth_live_FAKE",
    baseUrl: "https://example.test",
    fetchImpl,
  });
  assert.equal(result.outcome, "attested");
  assert.equal(result.status, 201);
  assert.equal(result.attestationId, "att_2026-04-27T12_xyz");

  assert.equal(observed.url, "https://example.test/api/v1/attest");
  assert.equal(observed.init.method, "POST");
  const body = JSON.parse(observed.init.body);
  assert.equal(body.agentId, "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee");
  assert.equal(body.actionType, "MY_ACTION");
  assert.equal(body.input, "hello");
  assert.equal(body.output, "world");
  assert.equal(body.policyId, "atap-basic");
  assert.equal(body.policyVersion, "1.0");
});

test("attestAction respects custom policyId / policyVersion", async () => {
  let observed = null;
  const fetchImpl = async (_url, init) => {
    observed = init;
    return { status: 201, text: async () => "{}" };
  };
  await attestAction({
    agentId: "x",
    actionType: "Y",
    input: "",
    output: "",
    policyId: "atap-high-risk",
    policyVersion: "2.0",
    apiKey: "k",
    fetchImpl,
  });
  const body = JSON.parse(observed.body);
  assert.equal(body.policyId, "atap-high-risk");
  assert.equal(body.policyVersion, "2.0");
});

test("attestAction maps non-2xx → outcome 'error'", async () => {
  const fetchImpl = async () => ({
    status: 400,
    text: async () =>
      JSON.stringify({ message: "Agent not found", code: "VALIDATION_ERROR" }),
  });
  const r = await attestAction({
    agentId: "missing",
    actionType: "Y",
    input: "",
    output: "",
    apiKey: "k",
    fetchImpl,
  });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 400);
  assert.equal(r.attestationId, null);
});

test("attestAction maps network failure → outcome 'error' (no throw)", async () => {
  const fetchImpl = async () => {
    throw new Error("ECONNREFUSED");
  };
  const r = await attestAction({
    agentId: "x",
    actionType: "Y",
    input: "",
    output: "",
    apiKey: "k",
    fetchImpl,
  });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 0);
  assert.match(r.body.error, /ECONNREFUSED/);
});

test("attestAction throws on missing required args", async () => {
  await assert.rejects(() =>
    attestAction({ agentId: "x", actionType: "Y", input: "", output: "", fetchImpl: () => {} }),
  /apiKey/);
  await assert.rejects(() =>
    attestAction({ agentId: "x", actionType: "Y", output: "", apiKey: "k", fetchImpl: () => {} }),
  /input/);
});

// ─── listAgents / getAgent ───────────────────────────────────────────

test("listAgents returns the parsed array on 200", async () => {
  const fetchImpl = async (_url, init) => {
    assert.equal(init.method, "GET");
    assert.equal(init.headers.Authorization, "Bearer alth_live_FAKE");
    return {
      status: 200,
      text: async () =>
        JSON.stringify([
          { agentId: "urn:uuid:a", name: "Alice", agentType: "custom", riskClassification: "high", status: "active" },
          { agentId: "urn:uuid:b", name: "Bob", agentType: "custom", riskClassification: "limited", status: "active" },
        ]),
    };
  };
  const r = await listAgents({ apiKey: "alth_live_FAKE", baseUrl: "https://example.test", fetchImpl });
  assert.equal(r.outcome, "ok");
  assert.equal(r.status, 200);
  assert.equal(r.agents.length, 2);
  assert.equal(r.agents[0].agentId, "urn:uuid:a");
});

test("listAgents maps non-2xx → outcome 'error', empty agents", async () => {
  const fetchImpl = async () => ({
    status: 401,
    text: async () => JSON.stringify({ message: "Unauthorized" }),
  });
  const r = await listAgents({ apiKey: "k", fetchImpl });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 401);
  assert.deepEqual(r.agents, []);
});

test("getAgent returns the agent on 200", async () => {
  const fetchImpl = async (url) => {
    assert.match(url, /\/api\/v1\/agents\/urn%3Auuid%3Atest$/);
    return {
      status: 200,
      text: async () =>
        JSON.stringify({
          agentId: "urn:uuid:test",
          name: "Test",
          agentType: "custom",
          riskClassification: "limited",
          status: "active",
        }),
    };
  };
  const r = await getAgent({ agentId: "urn:uuid:test", apiKey: "k", fetchImpl });
  assert.equal(r.outcome, "ok");
  assert.equal(r.agent.name, "Test");
});

test("getAgent maps 404 → outcome 'not-found' with agent=null", async () => {
  const fetchImpl = async () => ({
    status: 404,
    text: async () => JSON.stringify({ code: "NOT_FOUND", message: "Agent not found: urn:uuid:nope" }),
  });
  const r = await getAgent({ agentId: "urn:uuid:nope", apiKey: "k", fetchImpl });
  assert.equal(r.outcome, "not-found");
  assert.equal(r.status, 404);
  assert.equal(r.agent, null);
  // Body still parsed so callers can dig if they want
  assert.equal(r.body.code, "NOT_FOUND");
});

test("getAgent throws on missing args", async () => {
  await assert.rejects(() => getAgent({ apiKey: "k", fetchImpl: () => {} }), /agentId/);
  await assert.rejects(() => getAgent({ agentId: "x", fetchImpl: () => {} }), /apiKey/);
});

// ─── signResponse ───────────────────────────────────────────────────

test("signResponse 200 → outcome 'signed' with stampId + evidenceUrl", async () => {
  let observedBody = null;
  const fetchImpl = async (url, init) => {
    assert.equal(url, "https://example.test/api/sign");
    assert.equal(init.method, "POST");
    observedBody = JSON.parse(init.body);
    return {
      status: 200,
      text: async () =>
        JSON.stringify({
          id: 110,
          uuid: "4ed6bbec-5f99-421c-8680-c2aad89dc65f",
          responseHash: "abc123",
          signature: "base64sig",
          tsaToken: "base64tsa",
          model: "external",
          policyVersion: "1.0",
          createdAt: "2026-04-27T12:00:00Z",
        }),
    };
  };
  const r = await signResponse({
    response: "Hello",
    prompt: "Hi",
    apiKey: "alth_live_FAKE",
    baseUrl: "https://example.test",
    fetchImpl,
  });
  assert.equal(r.outcome, "signed");
  assert.equal(r.status, 200);
  assert.equal(r.stampId, 110);
  assert.equal(r.uuid, "4ed6bbec-5f99-421c-8680-c2aad89dc65f");
  assert.equal(r.responseHash, "abc123");
  assert.equal(r.signature, "base64sig");
  assert.equal(r.tsaToken, "base64tsa");
  assert.equal(r.evidenceUrl, "https://example.test/api/ai/evidence/110?format=zip");

  // body shape sent to server
  assert.equal(observedBody.response, "Hello");
  assert.equal(observedBody.prompt, "Hi");
  assert.equal(observedBody.policyId, "atap-basic");   // applied default
  assert.equal(observedBody.policyVersion, "1.0");      // applied default
});

test("signResponse drops undefined optional fields (no modelId/prompt → server defaults)", async () => {
  let observedBody = null;
  const fetchImpl = async (_url, init) => {
    observedBody = JSON.parse(init.body);
    return { status: 200, text: async () => JSON.stringify({ id: 1 }) };
  };
  await signResponse({ response: "x", apiKey: "k", fetchImpl });
  assert.equal("modelId" in observedBody, false);
  assert.equal("prompt" in observedBody, false);
  assert.equal(observedBody.response, "x");
});

test("signResponse maps 413 → outcome 'error' with parsed hint", async () => {
  const fetchImpl = async () => ({
    status: 413,
    text: async () =>
      JSON.stringify({ error: "Payload too large", hint: "Hash the response locally" }),
  });
  const r = await signResponse({ response: "huge".repeat(200_000), apiKey: "k", fetchImpl });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 413);
  assert.equal(r.stampId, null);
  assert.equal(r.evidenceUrl, null);
  assert.match(r.body.hint, /Hash the response/);
});

test("signResponse network failure → outcome 'error' (no throw)", async () => {
  const fetchImpl = async () => { throw new Error("ECONNREFUSED"); };
  const r = await signResponse({ response: "x", apiKey: "k", fetchImpl });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 0);
  assert.match(r.body.error, /ECONNREFUSED/);
});

test("signResponse throws on missing required args", async () => {
  await assert.rejects(() => signResponse({ apiKey: "k", fetchImpl: () => {} }), /response/);
  await assert.rejects(() => signResponse({ response: "x", fetchImpl: () => {} }), /apiKey/);
  await assert.rejects(() => signResponse({ response: "", apiKey: "k", fetchImpl: () => {} }), /response/);
});

// ─── verifyEvidence ─────────────────────────────────────────────────

/**
 * Produces a self-consistent .aep test bundle the way the backend would.
 * Mirrors AiEvidenceController + SignatureServiceImpl with one quirk:
 * Java's hand-rolled DigestInfo omits the standard NULL parameters in
 * the SHA-256 AlgorithmIdentifier, and verifyEvidence is built to
 * tolerate that. We replicate the non-standard form here so the
 * test exercises the production code path.
 */
function buildTestBundle({ response = "test response\n", composite = true, tamper = null } = {}) {
  const { privateKey, publicKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 2048 });
  const publicKeyPem = publicKey.export({ type: "spki", format: "pem" });

  const responseCanonical = Buffer.from(response, "utf8");
  const claimEnvelope = Buffer.from(
    '{"claim":"","confidence":0.000000,"model":"external","policy_version":"1.0"}',
    "utf8",
  );
  const canonical = composite
    ? Buffer.concat([responseCanonical, Buffer.from("\n"), claimEnvelope])
    : responseCanonical;
  const hashBytes = crypto.createHash("sha256").update(responseCanonical).digest();
  const hashHex = hashBytes.toString("hex");

  // Non-standard DigestInfo (matches the Java backend; omits NULL params).
  const digestInfoNonStandard = Buffer.concat([
    Buffer.from("302f300b0609608648016503040201", "hex"), // SEQ(47), SEQ(11), OID id-sha256 (no NULL)
    Buffer.from("0420", "hex"),                            // OCTET STRING (32)
    hashBytes,
  ]);
  const signature = crypto.privateEncrypt(
    { key: privateKey, padding: crypto.constants.RSA_PKCS1_PADDING },
    digestInfoNonStandard,
  );

  const zip = new AdmZip();
  zip.addFile("response.txt", responseCanonical);
  zip.addFile("canonical.bin", canonical);
  zip.addFile("hash.sha256", Buffer.from(hashHex));
  zip.addFile("signature.sig", Buffer.from(signature.toString("base64")));
  // Non-empty placeholder for the TSA token (base64 "fou"); verifyEvidence
  // only checks presence + non-empty, not RFC 3161 chain validity.
  zip.addFile("timestamp.tsr", Buffer.from("Zm91"));
  zip.addFile("metadata.json", Buffer.from(JSON.stringify({ model: "external", policyVersion: "1.0" })));
  zip.addFile("public_key.pem", Buffer.from(publicKeyPem));

  if (tamper) tamper(zip);

  return zip.toBuffer();
}

async function writeBundle(buf) {
  const dir = await mkdtemp(path.join(tmpdir(), "eatf-cli-verify-test-"));
  const file = path.join(dir, "evidence.aep");
  await writeFile(file, buf);
  return file;
}

test("verifyEvidence accepts a self-consistent composite bundle", async () => {
  const file = await writeBundle(buildTestBundle({ composite: true }));
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "valid");
  assert.equal(r.responseCanonicalBytes, "test response\n".length);
  assert.ok(r.unsignedSuffixBytes > 0, "composite bundle should report unsigned suffix");
  assert.equal(r.metadata.model, "external");
});

test("verifyEvidence accepts a sign-only bundle (canonical.bin == response_canonical)", async () => {
  const file = await writeBundle(buildTestBundle({ composite: false }));
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "valid");
  assert.equal(r.unsignedSuffixBytes, 0);
});

test("verifyEvidence reports missing-files when entries are dropped", async () => {
  const file = await writeBundle(
    buildTestBundle({
      tamper: (zip) => {
        zip.deleteFile("signature.sig");
      },
    }),
  );
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "missing-files");
  assert.deepEqual(r.missing, ["signature.sig"]);
});

test("verifyEvidence reports hash-mismatch when hash.sha256 was overwritten", async () => {
  const file = await writeBundle(
    buildTestBundle({
      tamper: (zip) => {
        zip.updateFile("hash.sha256", Buffer.from("0".repeat(64)));
      },
    }),
  );
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "hash-mismatch");
  assert.equal(r.expectedHash, "0".repeat(64));
});

test("verifyEvidence reports signature-invalid when signature was replaced", async () => {
  const file = await writeBundle(
    buildTestBundle({
      tamper: (zip) => {
        zip.updateFile("signature.sig", Buffer.from("AAAA".repeat(85)));
      },
    }),
  );
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "signature-invalid");
});

test("verifyEvidence reports tsa-empty when timestamp.tsr is zero-length", async () => {
  const file = await writeBundle(
    buildTestBundle({
      tamper: (zip) => {
        zip.updateFile("timestamp.tsr", Buffer.alloc(0));
      },
    }),
  );
  const r = await verifyEvidence({ path: file });
  assert.equal(r.outcome, "tsa-empty");
});

test("verifyEvidence throws when the path is missing", async () => {
  await assert.rejects(() => verifyEvidence({ path: "/nonexistent/path.aep" }), /ENOENT/);
});

// ─── probeBackend ───────────────────────────────────────────────────

test("probeBackend reports 'reachable' on 200", async () => {
  const fetchImpl = async (url) => {
    assert.equal(url, "https://example.test/");
    return { status: 200, text: async () => "" };
  };
  const r = await probeBackend({ baseUrl: "https://example.test", fetchImpl });
  assert.equal(r.outcome, "reachable");
  assert.equal(r.status, 200);
  assert.ok(r.latencyMs >= 0);
});

test("probeBackend treats 3xx (auth-redirect) as reachable", async () => {
  const fetchImpl = async () => ({ status: 307, text: async () => "" });
  const r = await probeBackend({ baseUrl: "https://example.test", fetchImpl });
  assert.equal(r.outcome, "reachable");
  assert.equal(r.status, 307);
});

test("probeBackend reports 'error' on 5xx", async () => {
  const fetchImpl = async () => ({ status: 503, text: async () => "" });
  const r = await probeBackend({ baseUrl: "https://example.test", fetchImpl });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 503);
});

test("probeBackend reports 'error' on network failure (no throw)", async () => {
  const fetchImpl = async () => { throw new Error("ECONNREFUSED"); };
  const r = await probeBackend({ baseUrl: "https://nope.invalid", fetchImpl });
  assert.equal(r.outcome, "error");
  assert.equal(r.status, 0);
  assert.match(r.error, /ECONNREFUSED/);
});

test("probeBackend honours custom path", async () => {
  let observed = null;
  const fetchImpl = async (url) => {
    observed = url;
    return { status: 200, text: async () => "" };
  };
  await probeBackend({ baseUrl: "https://example.test", path: "/healthz", fetchImpl });
  assert.equal(observed, "https://example.test/healthz");
});
