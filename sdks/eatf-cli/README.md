# `@eatf/cli`

Command-line tool for the EATF (Agent Trust Framework) agent
registry. Idempotently syncs an `agent.yaml` manifest into the EATF backend
via `PUT /api/v1/agents/{agentId}`.

Step 2 of the AEP **manifest pattern** (see the
[AEP profile v1 spec](https://github.com/tyche-institute/eatf/blob/main/specs/aep-profile-v1.md)
for the schema). Step 1 is the backend endpoint (already merged); this
package is its consumer.

## Why

The legacy onboarding flow involves five UI steps and three documented
gotchas around tenant scoping and key visibility. `@eatf/cli` collapses it
to two commands a partner can drop into any CI pipeline:

```bash
npx -y @eatf/cli@latest init my-agent              # writes agent.yaml
EATF_API_KEY=alth_live_... npx -y @eatf/cli@latest agents sync agent.yaml
```

The first run creates the agent on the API key's tenant; subsequent runs
patch mutable fields in place. Same call from a different tenant's API key
returns 409 — it is impossible to "lose" the agent or accidentally
double-register it on the wrong tenant.

## Install

Requires Node 20 or later. No build step — ships as plain ESM.

```bash
npm install -g @eatf/cli      # global
# or
npx -y @eatf/cli@latest        # one-shot
```

## Usage

```bash
eatf init <slug> [--out <path>]            # scaffold a fresh agent.yaml
eatf agents sync <manifest.yaml>           # PUT it to the registry
eatf list [--json]                         # list agents on the API key's tenant
eatf get <agent-id> | --manifest <path>    # fetch one agent's details
eatf attest --agent-id <urn>|--manifest <p> --action <type> \
            --input <text>|--input-file <p> \
            --output <text>|--output-file <p> \
            [--policy-id atap-basic] [--policy-version 1.0]
eatf sign   --response <text>|--response-file <p> \
            [--prompt <text>|--prompt-file <p>] \
            [--model-id external] [--policy-id atap-basic] \
            [--download <path>]            # write .aep evidence bundle to <path>
eatf verify <evidence.aep>                 # offline structural + crypto verify
eatf doctor [--manifest <path>]            # diagnose env/net/auth/tenant/agent/attest
eatf --version                             # print package version
eatf --help                                # full help
```

`eatf init <slug>` writes a commented `agent.yaml` template in the current
directory (override with `--out`) with a freshly-generated placeholder
`agentId`. It refuses to overwrite an existing file — pick a different
`--out` or remove the old one. The slug must match `[a-zA-Z0-9][a-zA-Z0-9._-]*`
and only seeds `displayName`; the URN is the stable identity. For new
agents the backend rewrites the `agentId` into the tenant-bound form
`urn:eatf:tenant:<tenantId>:agent:<slug>` on first registration; the
placeholder is only used until the server response is applied.

| Env var         | Default                        | Purpose                                |
| --------------- | ------------------------------ | -------------------------------------- |
| `EATF_API_KEY`  | (required)                     | Bearer token, `alth_live_...`.         |
| `EATF_BASE_URL` | `https://api.eatf.eu`     | EATF backend root.                     |

Exit codes:

| Code | Meaning                                                                |
| ---- | ---------------------------------------------------------------------- |
| 0    | Agent created (HTTP 201) or patched in place (HTTP 200).               |
| 1    | Cross-tenant conflict (HTTP 409), or any other HTTP/network failure.   |
| 2    | Invalid CLI arguments or unreadable / invalid manifest.                |

## Manifest format

```yaml
# Required
agentId: urn:eatf:tenant:8c14b7e0-1b6a-4f3e-9d31-2d62a1b27e45:agent:eu-ai-act-advisor
                                                          # tenant-bound stable id (Phase 2 v0.1+)
displayName: EU AI Act Advisor
agentType: custom                                        # custom | conversational | autonomous | ...
riskClassification: high                                 # minimal | limited | high

# Optional
description: Demo agent for Regulation (EU) 2024/1689
organization: Aletheia
contactEmail: demo@example.org
capabilities:
  - regulatory-qa
  - human-in-the-loop
  - evidence-package
eidasLevel: qualified                                    # simple | advanced | qualified
eidasCertificateArn: pki:cert:ABC123                     # optional pre-existing cert
signatureAlgorithm: HYBRID                               # HYBRID | RSA | ML-DSA
mcpDid: did:mcp:...                                      # optional MCP-I identity
primaryJurisdiction: EU
transactionLimit: 0
transactionCurrency: EUR
```

Three formats are accepted for `agentId`:

- **Tenant-bound** (recommended; Phase 2 v0.1+) —
  `urn:eatf:tenant:<tenantId>:agent:<slug>`. The backend mints this
  shape automatically for new registrations and the slug is the
  sanitised lowercase form of `displayName`. Tenant-bound URNs make
  structural independence visible at the identifier level and
  unblock policy-evaluation hooks on the attest path.
- **Legacy UUID** — `urn:uuid:<uuid>`. Recognised for backwards
  compatibility with agents registered before the tenant-bound
  scheme; verifiers accept both forms.
- **Caller-supplied namespaced slug** (e.g. `acme:fraud-detector`)
  for partner integrations that already publish their own stable
  identifier scheme. Namespacing prevents cross-tenant collisions.

## Programmatic API

Same package, ESM imports:

```js
import { readManifest, syncAgent } from "@eatf/cli";

const manifest = await readManifest("./agent.yaml");
const result = await syncAgent({
  manifest,
  apiKey: process.env.EATF_API_KEY,
  // baseUrl optional; defaults to https://api.eatf.eu
});

console.log(result.outcome);  // "created" | "updated" | "conflict" | "error"
console.log(result.status);   // HTTP status code
```

## Smoke test against the live demo

The `eu-ai-act-agent` partner integration is the manifest pattern's first
real consumer. Once `partner-integrations/eu-ai-act-agent/agent.yaml`
ships, you'll be able to run the loop yourself:

```bash
cd partner-integrations/eu-ai-act-agent
EATF_API_KEY=alth_live_... npx @eatf/cli agents sync agent.yaml
# [+] CREATED urn:uuid:d11c3f17-... (201 https://api.eatf.eu)
#     name=EU AI Act Advisor tenantId=4 eidasCertificate=pki:cert:...

EATF_API_KEY=alth_live_... npx @eatf/cli agents sync agent.yaml
# [~] UPDATED urn:uuid:d11c3f17-... (200 https://api.eatf.eu)
#     name=EU AI Act Advisor tenantId=4 eidasCertificate=pki:cert:...
```

## Tests

```bash
npm install
npm test
```

The unit suite stubs `fetch` and covers manifest validation, body
translation, the 201 / 200 / 409 / network-error outcome mapping, and URL
encoding for namespaced slugs. There is no test against a live backend; do
that by hand with the smoke commands above.

## License

Apache-2.0.
