# MCP Attestation Profile, v1

**Version:** 1.0-draft, dated 2026-05-12. Comment period open through 2026-08-12.
**Stable identifier:** `urn:eatf:spec:mcp-attest:1.0`
**Status:** technical specification for the EATF MCP Gateway (Phase 2.1) and any
compatible third-party gateway that wraps a downstream
[Model Context Protocol](https://modelcontextprotocol.io/) server and emits
cryptographic attestations for every `tool_call`.
**Owner:** EATF.eu maintainer team. Phase 2 step 2.1 of the EATF roadmap.
**Builds on:** `urn:eatf:spec:aep:1.0` (`docs/specs/aep-profile-v1.md`).

---

## 1. Purpose and audience

This profile specifies how an EATF-compatible **MCP gateway** observes,
canonicalises, and attests every `tool_call` that flows between an MCP host
(Cursor, Claude Desktop, Claude Code, a custom agent runtime) and one or more
downstream MCP servers. Where the [AEP profile v1](aep-profile-v1.md) defines
the byte-level contents of an `.aep` evidence package, *this* profile defines
the **upstream production rules**: what the gateway captures, how it binds an
MCP-layer identity to an EATF agent, when an attestation may block a call, and
how the resulting bytes feed into a v1 AEP container.

Audience: (1) **gateway implementers** building proxies, sidecars, or
local supervisors between MCP hosts and servers; (2) **MCP server authors**
shipping "first-class attested" builds suitable for EU AI Act Article 12
logging; (3) **auditors and regulators** consuming `.aep` packages claiming
conformance to this profile.

The goal of v1 is to make EATF attestation the **default trust substrate** for
the MCP ecosystem — analogous to Let's Encrypt for TLS. Any gateway can
implement this profile without an EATF license; the EATF reference gateway
is one conformant implementation among many. This document does **not**
replace, fork, or modify the upstream MCP specification — it is a
wire-compatible extension (see section 12).

## 2. Terminology

| Term | Definition |
|---|---|
| **MCP host** | The process that hosts an LLM agent and initiates `tool_call`s. Examples: Cursor, Claude Desktop, Claude Code, a custom Python runtime using `mcp.client.stdio`. |
| **MCP server** | A process that implements the MCP server side and exposes one or more tools (`tools/list`, `tools/call`). May run as stdio subprocess or HTTP endpoint. |
| **Tool call** | A single round-trip `tools/call` request/response pair, as defined by the MCP spec (`method: "tools/call"`, params `{ name, arguments }`). |
| **Gateway proxy** | The EATF-conformant process that sits transparently between host and server, observing every JSON-RPC frame and emitting attestations. May itself appear as an MCP server to the host (transparent passthrough) or as an MCP client to the downstream server, or both. |
| **Attestation** | The signed, timestamped record produced by the gateway for one tool call. Encoded as a v1 AEP container (see section 4) with an `mcp_attestation.json` entry plus the standard `.aep` envelope. |
| **Attestation mode** | `sign` (fire-and-forget) or `attest` (policy-evaluated, possibly blocking). See section 6. |
| **Cascading tool call** | A tool call made by a server-side agent that was itself triggered by a prior tool call. The child attestation MUST reference the parent via `parent_attestation_id`. |
| **EATF-registered agent** | An agent identity that exists in the EATF tenant's agent registry, addressable by URN (`urn:eatf:agent:<slug>`). |
| **Identity binding** | The deterministic mapping from an MCP-layer principal (host id + agent token + tenant key) to an EATF-registered agent URN. See section 9. |

## 3. Architecture

```
   ┌─────────────────────────┐
   │   MCP Host              │
   │   (Cursor / Claude      │
   │    Desktop / Code)      │
   └─────────────┬───────────┘
                 │  JSON-RPC over stdio or HTTP
                 │  (vanilla MCP frames)
                 ▼
   ┌─────────────────────────────────────────────┐
   │       EATF MCP Gateway (this profile)       │
   │                                             │
   │   1. Frame parser  ──────►  identity bind   │
   │   2. Policy eval   ──────►  decision        │
   │   3. Canonicaliser ──────►  canonical.bin   │
   │   4. Signer        ──────►  RSA + ML-DSA    │
   │   5. TSA stamper   ──────►  timestamp.tsr   │
   │   6. Ledger writer ──────►  hash-chained    │
   │                                             │
   │   Emits .aep with mcp_attestation.json      │
   └────────────┬────────────────────┬───────────┘
                │ (sign mode:        │ (attest mode:
                │  forwards always)  │  may block)
                ▼                    ▼
   ┌─────────────────────────────────────────────┐
   │  Downstream MCP server(s)                   │
   │  (filesystem, github, sql, custom, ...)     │
   └─────────────────────────────────────────────┘
```

The gateway terminates **two MCP sessions**:

- An **inbound** session in which the host treats the gateway as a regular MCP
  server. The host calls `initialize`, `tools/list`, `tools/call`, etc. and
  the gateway answers.
- One or more **outbound** sessions to downstream MCP servers. The gateway is
  an MCP **client** to each downstream server and forwards (or rewrites)
  frames as policy dictates.

Tool listings are **merged**: `tools/list` on the inbound side returns the
union of (downstream-server tools, gateway-native tools — see section 8),
with optional namespacing (`server-id__tool-name`) when collisions occur.
Namespacing rules MUST be documented in the gateway's published manifest.

Attestation hooks fire at three points:

1. **Pre-call.** After the gateway receives `tools/call` from the host but
   before forwarding to the downstream server. In `attest` mode the policy
   engine runs here and MAY refuse, transform, or escalate the call.
2. **Post-call.** After the downstream server returns. The gateway has both
   `arguments` and `result` available; the attestation is built and signed.
3. **Streaming chunk.** For long-running tool calls that emit `notifications`
   or partial results (section 7), one chunk attestation per frame.

The reference gateway implementation lives at
`backend/src/main/java/ai/aletheia/mcp/Gateway*.java` (Phase 2.1) and
`partner-integrations/aletheia-mcp-server/` contains the stdio reference
adapter used by Cursor.

## 4. Canonical form for tool_call attestation

Every attestation is bound to a deterministic byte sequence,
`canonical.bin`, in the spirit of AEP profile v1 section 6.
Canonicalisation identifier: `eatf-mcp-canonical-1`. Rules:

1. **Build `mcp_attestation.json`** per section 5. Unknown fields are
   permitted (JCS reorders anyway).
2. **JCS-encode** per RFC 8785: keys sorted by Unicode codepoint
   recursively; no insignificant whitespace; no BOM; UTF-8; numbers per
   ECMA-404 with no trailing zeros; string escapes minimal per RFC 8259.
3. **Canonical bytes = the JCS output**, and only that. Unlike AEP v1
   there is no `response.txt` prefix; the narrative lives inside
   `tool_result_canonical` (or its hash).
4. **Hash and sign.** SHA-256 over `canonical.bin`; RSA-4096 signature;
   ML-DSA-65 when PQC mode is on (AEP v1 section 3).
5. **Wrap in `.aep`** per AEP profile section 2, with this file layout:

```
attestation_<id>.aep   (ZIP, flat layout)
├── mcp_attestation.json   (this profile)
├── canonical.bin          (JCS output, the bytes hashed/signed)
├── hash.sha256            (lower-case hex SHA-256 of canonical.bin)
├── signature.sig          (Base64 RSA-4096 signature)
├── public_key.pem
├── signature_pqc.sig      (when PQC enabled)
├── pqc_public_key.pem
├── pqc_algorithm.json
├── timestamp.tsr          (Base64 RFC 3161 token over hash.sha256)
├── metadata.json          (AEP v1 envelope metadata)
└── policy_coverage.json   (attest mode only)
```

The AEP envelope `metadata.json` MUST set `canonicalisation` to
`eatf-mcp-canonical-1`; presence of `mcp_attestation.json` signals this
profile applies. A minimal example (formatted for legibility — actual JCS
bytes have no whitespace):

```json
{
  "agent_uri": "urn:eatf:agent:repo-bot-alpha",
  "gateway_id": "urn:eatf:gateway:eatf-eu-prod-01",
  "host_id": "urn:eatf:host:cursor:9a7b1c2d",
  "mcp_protocol_version": "2024-11-05",
  "mode": "sign",
  "parent_attestation_id": null,
  "policy_id": null,
  "policy_version": null,
  "request_id": "req_01HXY7Z3JKQ1A2B3C4D5E6F7G8",
  "schema": "urn:eatf:spec:mcp-attest:1.0",
  "timestamp": "2026-05-12T11:23:45.812Z",
  "tool_arguments_canonical": "{\"path\":\"/etc/passwd\"}",
  "tool_name": "filesystem.read_file",
  "tool_result_canonical": "{\"content\":\"root:x:0:0:root:/root:/bin/bash\\n\"}"
}
```

## 5. Required metadata fields

`mcp_attestation.json` is the heart of every attestation. v1 fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `schema` | string | yes | MUST equal `urn:eatf:spec:mcp-attest:1.0`. |
| `mcp_protocol_version` | string | yes | The MCP protocol version negotiated during `initialize`, e.g. `"2024-11-05"`. Verbatim from the host-server handshake. |
| `host_id` | URN | yes | Identifier of the MCP host process. Format: `urn:eatf:host:<host-class>:<machine-uuid-hash>` where `<host-class>` is a registered identifier (`cursor`, `claude-desktop`, `claude-code`, `custom`) and `<machine-uuid-hash>` is the first 16 hex chars of `SHA-256(machine_uuid ‖ tenant_salt)`. The raw machine UUID MUST NOT appear. |
| `agent_uri` | URN | yes | URN of the EATF-registered agent, e.g. `urn:eatf:agent:devops-runbook-bot`. The gateway resolved this via identity binding (section 9). |
| `gateway_id` | URN | yes | Identifier of the gateway instance, e.g. `urn:eatf:gateway:eatf-eu-prod-01`. Stable across restarts; bound to the signing key. |
| `tool_name` | string | yes | The MCP tool name as it appears in the downstream server's `tools/list`. When the gateway namespaces (e.g. `github__create_issue`), the namespaced form is recorded here and the un-namespaced form goes into `tool_name_raw`. |
| `tool_name_raw` | string | no | The un-namespaced tool name when namespacing was applied. |
| `tool_arguments_canonical` | string | yes | The JCS form of the arguments object. Stored as an escaped JSON string so the outer attestation remains a flat JSON document; verifiers re-parse it. |
| `tool_result_canonical` | string \| null | conditional | The JCS form of the tool result. MUST be present unless `tool_result_hash` is set. When the JCS result exceeds 1 MiB, set this field to `null` and set `tool_result_hash` instead. For tool calls that did not return (error / blocked), set this to `null` and set `error` instead. |
| `tool_result_hash` | string | conditional | Lower-case hex SHA-256 of the JCS-canonical result bytes. Used when the result exceeds 1 MiB. The full result bytes MUST be persisted by the gateway for at least the retention period defined in the deployment's Framework Operations Statement and made available to verifiers on request. |
| `request_id` | string | yes | The MCP-layer JSON-RPC `id` (string form) used by the host for this `tools/call`. Free-form per MCP; preserved verbatim. |
| `timestamp` | RFC 3339 | yes | UTC instant when the gateway built the canonical bytes. Millisecond precision required; sub-millisecond optional. The gateway clock SHOULD be synced via NTP and is subject to the ±2-second drift bound documented in AEP v1 section 7. |
| `mode` | string | yes | Either `"sign"` or `"attest"`. See section 6. |
| `policy_id` | string \| null | conditional | MUST be set when `mode = "attest"`. Identifies the policy that evaluated the call (e.g. `atap-basic`). Null in `sign` mode. |
| `policy_version` | string \| null | conditional | MUST be set when `mode = "attest"`. Semantic version of the named policy (e.g. `"1.4"`). |
| `policy_decision` | string \| null | conditional | One of `allow`, `block`, `require_human_approval`, `transform`. MUST be set when `mode = "attest"`. |
| `parent_attestation_id` | string \| null | no | The `attestation_id` of the parent attestation when this tool call is a cascading child. Null otherwise. |
| `chunk_chain` | object \| null | no | Streaming chain metadata; see section 7. Null for non-streaming calls. |
| `error` | object \| null | no | Set when the tool call failed or was blocked. Shape: `{ "code": "<symbolic>", "message": "<human-readable>", "source": "downstream"\|"gateway"\|"policy" }`. |
| `tenant_id_hash` | string | yes | Same construction as AEP v1: SHA-256 of the tenant numeric id with the tenant salt. Never the raw id. |

Implementations MUST treat unknown fields as forward-compatible and preserve
them through any pass-through processing. The canonical hash is computed
over the JCS form, so any unknown field that survives JCS sort order is
covered by the signature.

An `attest`-mode example sets `policy_id`, `policy_version`,
`policy_decision` (e.g. `"require_human_approval"`), and an `error` object
with `source: "policy"` when the call is paused or blocked. The companion
`policy_coverage.json` (AEP v1 optional entry) lists, per rule, which
inputs were inspected, the rule output, and any external fetches the
policy made (with their attestation ids when those were themselves
attested).

## 6. Two attestation modes

A v1-conformant gateway MUST implement both modes and MUST select between
them per tenant, per agent, or per tool. The mode in effect for a given
call is recorded in `mcp_attestation.mode`.

### 6.1 `sign` mode (fire-and-forget)

Sub-millisecond on the call path: the gateway forwards immediately and
builds the attestation asynchronously after the response. **No** policy
evaluation; `policy_id`, `policy_version`, `policy_decision` are `null`.
Downstream calls are **always** forwarded; attestation production failures
(signing key unavailable, ledger write rejection) MUST be surfaced via the
operator console but MUST NOT block host-server traffic. Default for
read-only tools, telemetry, low-risk automation, and public demo gateways.

### 6.2 `attest` mode (policy-evaluated, may block)

Latency is bounded by policy-evaluation time plus, where required, human
approval latency. The gateway MAY hold the `tools/call` open via MCP
progress notifications or MAY return `error.code = "human_approval_pending"`
with an opaque resumption handle. Policy evaluation is mandatory; the
full trace is captured in `policy_coverage.json`. Exactly one
`policy_decision` is recorded:

- `allow` — forward as-is.
- `transform` — forward a modified arguments payload. The attestation's
  `tool_arguments_canonical` reflects the *forwarded* payload; the
  pre-transform form is preserved in `policy_coverage.json`.
- `require_human_approval` — pause the call; once approved (via the EATF
  console or `eatf.request_human_approval` — section 8) the gateway emits
  a follow-up attestation linked via `parent_attestation_id`.
- `block` — refuse. The host receives a JSON-RPC error (`code: -32001`)
  carrying the policy rationale; the attestation is still persisted.

If the policy engine itself fails the gateway MUST fail closed:
`error.source = "gateway"`, host receives a JSON-RPC error. Use cases:
money movement, PII access, production infrastructure, Article 6 EU AI
Act high-risk systems.

### 6.3 Selecting the mode

Mode is a deterministic function of `(tenant_id, agent_uri, tool_name)`.
The reference gateway resolves it via the tenant's governance config;
third-party gateways MAY use any deterministic rule provided it is
documented and exposed through introspection (section 8).

## 7. Streaming attestation

Some MCP tool calls produce results that are too large or too slow to fit a
single response — typical examples are file streams, log tails, and
incremental model outputs. The MCP spec supports this via progress
notifications and partial-result frames. The gateway attests such calls
with a **per-chunk hash chain** so that no chunk can be dropped, reordered,
or substituted without detection.

### 7.1 Wire pattern

For a streaming call, the gateway emits **one attestation per chunk** plus a
**final summary attestation** that closes the chain. Each chunk attestation
carries a `chunk_chain` field:

```json
"chunk_chain": {
  "stream_id": "stream_01HXY7Z3JKQ1A2B3C4D5E6F7G8",
  "chunk_index": 17,
  "chunk_hash": "9af1...d4c2",
  "previous_chunk_hash": "84bc...e210",
  "is_final": false
}
```

Rules: `stream_id` is a ULID shared by every chunk of a stream (distinct
from `request_id`); `chunk_index` is zero-based and monotonic;
`chunk_hash` is the lower-case hex SHA-256 over the JCS form of the chunk
payload; `previous_chunk_hash` is the prior `chunk_hash` (64 zeros for
index 0). The **final summary attestation** sets `is_final = true`,
`chunk_index = N` (one past the last data chunk), `chunk_hash` =
SHA-256 over the concatenation of every chunk's `chunk_hash` (a
Merkle-line construction), and `tool_result_canonical` = JCS of
`{"chunks": <n>, "bytes": <m>, "duration_ms": <t>}`. Intermediate chunks
MAY batch their ledger writes; the final attestation MUST be written
synchronously before the gateway returns.

### 7.2 Resumption

On interruption (host disconnect, downstream crash) the gateway MUST
still emit a final summary attestation with `is_final = true`,
`error.code = "stream_aborted"`, and an accurate `chunks` count.
Verifiers thus see a complete signed chain even for incomplete streams.

## 8. Gateway-as-MCP-server tools

A v1-conformant gateway MAY itself expose MCP tools to the host. When it
does, three tools are **reserved** by this profile and MUST behave per
their published JSON schemas. They are namespaced under `eatf.` to avoid
collisions with downstream-server tool names.

### 8.1 `eatf.attest_action`

Attest an action that did not flow through the proxy path (e.g. a side
effect performed by the host). Returns the `attestation_id`.

```json
{
  "name": "eatf.attest_action",
  "description": "Produce an EATF attestation for an action performed by the agent. Returns the attestation id and verification URL.",
  "inputSchema": {
    "type": "object",
    "required": ["action_type", "payload"],
    "properties": {
      "action_type": {"type": "string"},
      "payload": {"type": "object"},
      "mode": {"type": "string", "enum": ["sign", "attest"], "default": "sign"},
      "parent_attestation_id": {"type": ["string", "null"]}
    }
  }
}
```

### 8.2 `eatf.verify_record`

Verify an `.aep` by id. Returns parsed metadata, signature status, and
ledger inclusion proof. Read-only.

```json
{
  "name": "eatf.verify_record",
  "description": "Verify an EATF attestation record and return its validity, contents, and ledger inclusion proof.",
  "inputSchema": {
    "type": "object",
    "required": ["attestation_id"],
    "properties": {
      "attestation_id": {"type": "string"},
      "include_full_payload": {"type": "boolean", "default": false}
    }
  }
}
```

### 8.3 `eatf.request_human_approval`

Route an action through human review (useful when the agent itself
decides a step needs oversight). Blocks via MCP progress notifications
until a human responds or the deadline elapses.

```json
{
  "name": "eatf.request_human_approval",
  "description": "Pause execution and request a human approval. Returns once the human approves, rejects, or the deadline passes.",
  "inputSchema": {
    "type": "object",
    "required": ["action_type", "summary"],
    "properties": {
      "action_type": {"type": "string"},
      "summary": {"type": "string"},
      "payload": {"type": "object"},
      "deadline_seconds": {"type": "integer", "minimum": 1, "maximum": 86400, "default": 3600},
      "approvers": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```

A gateway MAY expose additional `eatf.*` tools (e.g. `eatf.list_policies`),
outside v1 conformance scope. New reserved names MUST be coordinated with
the EATF maintainer team.

## 9. Identity binding

The MCP spec deliberately does not standardise agent identity — each
host ships its own credential model. The gateway's job is to bind
whatever the host presents to an EATF-registered agent URN. v1 defines a
three-stage pipeline:

1. **Principal extraction.** From the transport layer:
   - **stdio:** `ALETHEIA_*` env vars (see
     `partner-integrations/aletheia-mcp-server/README.md`):
     `ALETHEIA_API_KEY` (preferred) or `ALETHEIA_EMAIL` +
     `ALETHEIA_PASSWORD` plus `ALETHEIA_AGENT_ID`.
   - **HTTP:** `Authorization: Bearer <EATF API key>` plus
     `X-EATF-Agent-Id`, `X-EATF-Host-Class`, `X-EATF-Host-Uuid-Hash`.
2. **Tenant-defined mapping.** One of `direct` (verbatim),
   `pattern` (regex/template over host metadata), `oidc-claim`
   (bearer-to-OIDC exchange, read `urn:eatf:agent` from a configured
   claim), or `manifest` (chained identity from a prior
   `agent_manifest.json`).
3. **Authorisation.** Verify the resolved agent URN is active in the
   tenant registry and authorised to invoke the tool. Failure →
   attestation with `policy_decision = "block"`,
   `error.code = "agent_not_authorised"`.

Mapping rules are tenant-scoped and versioned. The version in effect MUST
be recorded in `policy_coverage.json` (`attest` mode) or an
`identity_binding.json` AEP entry (`sign` mode with traceability on).

## 10. Transport bindings

The profile is transport-agnostic — `mcp_attestation.json` does not depend
on how frames reached the gateway — but each transport has wire details
that conformant gateways MUST honour.

### 10.1 stdio (default in 2025–2026)

Dominant production transport. The gateway spawns the downstream server as
a subprocess; inbound, the gateway either owns its own stdin/stdout (host
spawns it) or a Unix domain socket (sidecar mode). Wire format:
line-delimited JSON-RPC 2.0 per MCP. `host_id` from parent process
metadata (`host_class` ← executable name, `machine_uuid_hash` ←
`gethostuuid()`); `request_id` is the raw JSON-RPC id; streaming chunks
correspond to MCP `notifications/progress` frames with a matching
`progressToken`.

### 10.2 HTTP transport

For the long-lived HTTP transport (`2024-11-25-experimental` upstream),
the gateway terminates one HTTPS connection per session: JSON-RPC 2.0 over
POST plus SSE for streaming. `host_id` derives from the bearer token's
`aud` claim plus TLS SNI; when the host presents a client certificate the
SHA-256 fingerprint is concatenated into the hash. Streaming chunks map
to SSE `event: progress` lines.

### 10.3 Future: Anthropic A2A and OpenAI MCP fork

A2A (Anthropic, anticipated 2026 H2) is expected to share MCP's JSON-RPC
shape with added agent-level semantics. The OpenAI MCP fork (announced
2026 Q1) diverges in `tools/list` shape but preserves `tools/call`. v1
commits to: (a) treating any `method: tools/call` (or `agent/call` in
A2A) as attestable; (b) recording the transport in
`mcp_attestation.transport` (`"stdio"`, `"http"`, `"a2a"`, `"openai-mcp"`);
(c) not freezing wire compatibility — when those specs stabilise, a v1.1
profile will pin the mapping. Until then, gateways MAY attest A2A or
OpenAI-fork traffic but MUST flag `transport_experimental: true` in
`policy_coverage.json`.

## 11. Security considerations

The threat model below complements
`partner-integrations/aletheia-mcp-server/THREAT_MODEL.md` and
`docs/legal/threat-model.md`. Attacker capabilities are categorised by
where the attacker sits relative to the gateway.

### 11.1 What an attacker can do

- **Malicious MCP host.** Can send arbitrary `tools/call` payloads and
  forge MCP-layer identity claims. Mitigation: bearer-token authentication
  at the gateway boundary (section 9) — without a valid tenant credential
  the attacker reaches no downstream tools.
- **Malicious downstream server.** Can return crafted results to poison
  downstream LLM reasoning. Out of trust boundary; v1 still captures the
  raw bytes for forensic review.
- **Network attacker between host and gateway / gateway and downstream.**
  Mitigated by TLS (HTTP transport) or local IPC (stdio). Gateways SHOULD
  enforce TLS/mTLS on outbound traffic.
- **Compromised gateway operator.** Can produce false attestations or
  refuse to attest legitimate events. Mitigations: signature pinning to a
  published gateway key (AEP v1 section 8); per-tenant hash-chained ledger
  makes missing block indices detectable.

### 11.2 What an attacker cannot do

- **Forge a valid `.aep`.** RSA + ML-DSA signatures plus RFC 3161 timestamp
  anchor every attestation; verifiers reject mismatches.
- **Backdate.** The TSA token binds the canonical hash to TSA wall clock.
- **Replay as a different call.** `request_id`, `agent_uri`, `gateway_id`,
  and `timestamp` are inside the signed bytes; `(gateway_id,
  attestation_id)` is unique.
- **Hide a streaming chunk.** Per-chunk hash chain (section 7).
- **Substitute a historical ledger entry.** Hash chain breaks.

### 11.3 Out of scope

Prompt injection at the host level (gateway sees frames after the host
decides to call); side channels through policy-evaluation timing
(gateways processing high-sensitivity workloads SHOULD constant-time
their evaluator; v1 does not mandate this).

## 12. Interop with the Anthropic MCP standard

This profile is a **strict superset** of MCP at the wire level:

1. **Unaware hosts.** Talk to a gateway as if to a regular MCP server.
   `initialize`, `tools/list`, `tools/call` work unchanged; attestations
   are produced server-side.
2. **Unaware servers.** See a regular MCP client connection. No protocol
   extension required.
3. **Tool listing.** Reserved `eatf.*` tools appear alongside downstream
   tools; hosts that ignore them are fine.
4. **MCP-I compatibility.** MCP-I (see `docs/concepts/mcp-ecosystem.md`)
   serves as principal source in stage 1 of identity binding (section 9):
   `agent_uri` maps from the MCP-I DID. Recommended but not required.
5. **No spec fork.** No upstream message types are repurposed; no new
   `method:` strings outside the `eatf.*` namespace.

When the upstream MCP spec evolves non-backward-compatibly, a profile
v1.x revision will pin the corresponding `mcp_protocol_version` and any
wire adjustments. Gateways MUST record the negotiated
`mcp_protocol_version` so verifiers can dispatch correctly.

## 13. Conformance

A gateway is **v1-conformant** if it satisfies all of:

1. **Frame coverage.** Every `tools/call` frame with a successfully bound
   `agent_uri` produces exactly one terminal attestation (or, for
   streaming calls, a chunk-chain plus a final summary attestation).
2. **Canonicalisation.** `canonical.bin` is produced by
   `eatf-mcp-canonical-1` (section 4); independent re-canonicalisation
   yields byte-identical output.
3. **Signing.** RSA-4096 signature; ML-DSA-65 when PQC mode is on; keys
   per AEP v1 section 8.
4. **Timestamping.** RFC 3161 `timestamp.tsr` over `hash.sha256`.
5. **Modes.** Both `sign` and `attest` implemented; selection is
   deterministic per `(tenant, agent_uri, tool_name)`.
6. **Identity binding.** All three pipeline stages implemented; mapping
   rule version is recorded.
7. **Reserved tools.** `eatf.attest_action`, `eatf.verify_record`, and
   `eatf.request_human_approval` exposed (or documented as unavailable in
   read-only public deployments).
8. **Ledger.** Terminal attestations are written to a hash-chained
   tenant ledger per AEP v1 section 9.
9. **Test vectors.** Accepts the v1 corpus at
   `backend/src/test/resources/fixtures/mcp-attest/` with expected
   byte-for-byte outputs.

A gateway satisfying (1)–(4) and (8)–(9) but not yet `attest` mode is
**transitional conformant** — suitable for low-risk public deployments.
Anything else is **non-conformant**.

## 14. Open issues

1. **Google A2A alignment.** Google's Agent-to-Agent protocol (alpha as
   of 2026-04) overlaps in spirit but uses Protobuf. A mapping table from
   A2A `RunAgent` requests to `mcp_attestation.json` is tracked at
   `docs/research/a2a-mapping.md` (TBD).
2. **OpenAI MCP fork.** Keeps `tools/call` but reshapes `tools/list`;
   v1.1 will pin the mapping once the fork stabilises.
3. **A2P streaming semantics.** Anthropic's draft "Agent-to-Process"
   transport interleaves streams within a single `request_id`. Open:
   whether to add `stream_index` alongside `chunk_index`.
4. **Tool argument secrets.** Some tools accept secrets as arguments;
   attesting them verbatim leaks them. v1 leaves redaction to tenant
   policy (`transform` decisions); v1.1 may introduce a
   `tool_arguments_redacted` field with a hash commitment.
5. **Public-good gateway operations.** A globally trusted public gateway
   ("Let's Encrypt of MCP") raises operational questions: liability,
   key custody, governance. Tracked in
   `docs/legal/framework-operations.md` and the Phase 3 federation
   work; the technical profile is independent of their resolution.

## 15. Related documents

- `docs/specs/aep-profile-v1.md` — the underlying AEP container format.
  Every MCP attestation is delivered as a v1 AEP package.
- `docs/concepts/mcp-ecosystem.md` — positioning of EATF relative to
  MCP-I, Checkpoint, and other MCP ecosystem layers.
- `docs/legal/framework-operations.md` — Framework Operations
  Statement (replaces the earlier TSPS draft; EATF is not a trust
  service). References this profile as the production rule for
  MCP-derived attestations.
- `docs/legal/threat-model.md` — overall threat model for EATF.eu.
- `docs/specs/public-key-mirror.md` — gateway signing key history.
- `partner-integrations/aletheia-mcp-server/README.md` — reference stdio
  adapter and Cursor configuration.
- `partner-integrations/aletheia-mcp-server/THREAT_MODEL.md` — stdio
  adapter threat model, complementary to section 11.
- ETSI TR submission draft — Phase 2 step 2.13.

## 16. Changelog

| Version | Date | Notes |
|---|---|---|
| 1.0-draft | 2026-05-12 | Initial Phase 2 step 2.1 draft. Comment period open through 2026-08-12. |


