# AEP (Agent Evidence Package) Profile, v1

> **Operator update (2026-05-14).** This open specification is published
> by **Tyche Institute** (Estonian non-profit, registration in progress)
> for the EATF research project (also referred to as Aletheia AI).
> Compatible implementations are encouraged. This is a self-published
> research draft representing the maintainer's analysis; it does not
> constitute a formal commitment, regulatory filing, or legal opinion.
> Substantive byte-level rules are unchanged in this revision.

**Version:** 1.0-draft, dated 2026-05-12 (operator-entity revision 2026-05-14). Comment period open through 2026-08-12.
**Stable identifier:** `urn:eatf:spec:aep:1.0`
**Status:** open specification for the `.aep` evidence package emitted by the EATF reference implementation. Compatible implementations are encouraged.
**Owner:** Tyche Institute (Estonian non-profit, registration in progress), maintainer of the EATF research project.

---

## 1. Purpose

Define, at the byte level, the contents and canonicalisation rules of an
`.aep` (Aletheia Evidence Package) so an independent verifier can:

1. Recompute the canonical bytes from the included payload.
2. Verify the canonical-bytes hash matches the embedded `hash.sha256`.
3. Verify the embedded RSA signature against the embedded public key.
4. Verify the embedded ML-DSA-65 signature against the embedded PQC public key.
5. Parse the embedded RFC 3161 timestamp token and validate it.
6. Resolve the agent identity, model id, policy id, policy version, and
   attestation id without any network call.

This document is referenced from the EATF Framework Operations
Statement (`docs/legal/framework-operations.md`). The verifier reference
implementation lives in
`backend/src/main/java/ai/aletheia/verifier/EvidenceVerifierImpl.java`.

EATF is not an eIDAS trust service under Regulation (EU) 910/2014
Article 3(16); the AEP format documented here is a technical
self-attestation envelope, not a Qualified Electronic Attestation of
Attributes (QEAA) under Article 3(45).

## 2. Container format

A v1 `.aep` package is a **ZIP archive** (PKZIP, store or deflate). The
archive contains a flat directory of named files; nested directories
are forbidden in v1. Maximum uncompressed size: 10 MB (mirrors the
public verifier endpoint limit set in Phase 0 step 0.8).

The default file extension is `.aep`. Implementations MAY accept `.zip`
when the manifest is unambiguous.

## 3. Required entries

Every v1 package MUST include the following entries with these exact
names (case-sensitive, no path prefix):

| Entry | Content | Format |
|---|---|---|
| `response.txt` | The textual payload that was attested (the AI response text or governed action description). | UTF-8 text. No BOM. Line endings preserved as-issued. |
| `canonical.bin` | The canonical byte sequence produced from `response.txt` by the canonicalisation rules in section 4. Hash is computed over **these** bytes. | Opaque binary. |
| `hash.sha256` | Lower-case hex SHA-256 of `canonical.bin`. | ASCII, 64 hex characters, optional trailing newline. |
| `signature.sig` | Base64 (standard alphabet, with padding) of the PKCS#1 v1.5 RSA signature over `canonical.bin`. Inner digest algorithm: SHA-256. | ASCII. |
| `public_key.pem` | PEM-encoded RSA public key used to verify `signature.sig`. | ASCII, BEGIN/END PUBLIC KEY headers. |
| `metadata.json` | Machine-readable attestation metadata. See section 5. | UTF-8 JSON, canonicalised per section 4.4. |
| `timestamp.tsr` | Base64 of the RFC 3161 TimeStampToken issued for `hash.sha256` (the hex string is hashed again per RFC 3161 inside the TSA request; the verifier matches both). | ASCII. |

## 4. Optional entries (REQUIRED when PQC is enabled)

When the issuing TSP has `ai.aletheia.signing.pqc-enabled=true` (the
EATF default starting Phase 1.9), the following entries MUST be present:

| Entry | Content | Format |
|---|---|---|
| `signature_pqc.sig` | Base64 of the ML-DSA-65 signature over `canonical.bin`. | ASCII. |
| `pqc_public_key.pem` | PEM-encoded ML-DSA-65 public key. | ASCII, BEGIN/END PUBLIC KEY headers. |
| `pqc_algorithm.json` | JSON object describing the PQC algorithm: `{"algorithm":"ML-DSA-65","oid":"2.16.840.1.101.3.4.3.18","level":3}`. | UTF-8 JSON. |

A v1 package without PQC entries is valid for backward compatibility
with pre-Phase-1.9 deployments. A v2 (planned) will make PQC mandatory.

Other optional entries:

| Entry | Content |
|---|---|
| `policy_coverage.json` | Per-rule policy evaluation report (attest mode only). |
| `agent_manifest.json` | A snapshot of the agent identity manifest that authorised this attestation. |
| `disclosure.json` | Article 50 transparency disclosure metadata (Phase 2.6). |
| `overt_receipt.json` | OVERT 1.0 profile receipt binding the package hash, scope, subject, event, policy, and witness file references. |

### 4.1 `overt_receipt.json` schema

`overt_receipt.json` is an additive profile entry. It does not create a new
package type and does not replace any required `.aep` entry. Verifiers that do
not understand OVERT MAY ignore it; OVERT-aware verifiers MUST reject the
package if the receipt is present and inconsistent with the rest of the
package.

Minimum schema:

```json
{
  "overt": "1.0.0",
  "profile": "urn:eatf:spec:aep:1.0",
  "profile_revision": "1.0-draft",
  "scope": "foundational:aep-response",
  "subject": {
    "agent_id": "urn:eatf:tenant:<tenantId>:agent:<slug>",
    "tenant_hash": "sha256:<tenant-binding-hash>",
    "system": "eatf-aep",
    "revision": "1.0-draft"
  },
  "event": {
    "type": "eatf.response",
    "timestamp": "2026-05-14T12:00:00Z",
    "action_type": "sign"
  },
  "policy": {
    "id": "atap-basic",
    "version": "1.0",
    "coverage": 1.0,
    "decision": "allow"
  },
  "content_hash": "sha256:<64 lowercase hex chars from hash.sha256>",
  "prev": null,
  "witness": {
    "iap": "EATF.eu",
    "signature_refs": ["signature.sig"],
    "timestamp_refs": ["timestamp.tsr"]
  }
}
```

Required fields:

| Field | Requirement |
|---|---|
| `overt` | MUST equal `1.0.0` for this profile revision. |
| `profile` | MUST equal `urn:eatf:spec:aep:1.0`. |
| `profile_revision` | MUST identify the AEP draft/release that generated the receipt. |
| `scope` | MUST be a non-empty OVERT assessment scope string. Current EATF generators use `foundational:aep-response`, `agentic-extended:atap-action`, or `agentic-extended:mcp-tools-call`. |
| `subject.agent_id` | MUST match `metadata.json.agent_id` when metadata carries an agent identifier. MAY be `null` for sign-only response packages. |
| `subject.tenant_hash` | MUST match `metadata.json.tenant_id_hash` when present. MUST NOT contain a raw tenant id. |
| `event.timestamp` | MUST match `metadata.json.created_at` when present. |
| `event.action_type` | MUST match `metadata.json.action_type` when present. |
| `policy.version` | MUST match `metadata.json.policy_version` when present. |
| `policy.coverage` | MUST match `metadata.json.policy_coverage` when present. |
| `policy.decision` | SHOULD be `allow`, `deny`, or equivalent policy-engine status when metadata carries `policy_decision`; MUST match that metadata field when present. |
| `content_hash` | MUST equal `sha256:` followed by the lower-case value of `hash.sha256`. |
| `prev` | MAY be `null`; otherwise SHOULD name the previous attestation id or digest in an evidence chain. |
| `witness.iap` | MUST identify the independent attestation provider that issued or preserved the package. |
| `witness.signature_refs` | MUST be a non-empty array of flat filenames in the same package. Each referenced file MUST exist and be non-empty. |
| `witness.timestamp_refs` | MUST be an array of flat filenames in the same package. It MAY be empty for transitional packages without a timestamp. |

An OVERT-aware verifier MUST compare `content_hash` to `hash.sha256`, compare
the metadata-bound fields above, and confirm every referenced witness file is
present in the flat ZIP namespace. Unknown receipt fields MUST be ignored for
forward compatibility.

## 5. `metadata.json` schema

The metadata file is the primary integration point for downstream
tooling (CLI, WASM verifier, GRC connectors). v1 fields:

```json
{
  "schema": "urn:eatf:spec:aep:metadata:1.0",
  "attestation_id": "att_01HXY...ULID",
  "uuid": "0c45db8d-1bf2-4f7e-9c8f-f7e2c5f7f76e",
  "tenant_id_hash": "f3a1c7...",          // SHA-256 of the tenant numeric id; never the raw id
  "agent_id": "urn:eatf:tenant:<tenantId>:agent:medical-assistant-7a3c",
  "model": "gpt-4o-2025-08-06",
  "policy_id": "atap-basic",
  "policy_version": "1.0",
  "created_at": "2026-05-12T11:23:45Z",   // RFC 3339 / ISO 8601 UTC
  "canonicalisation": "eatf-canonical-1",
  "hash_algorithm": "SHA-256",
  "rsa_key_id": "kid_rsa_2026-01",
  "pqc_key_id": "kid_mldsa65_2026-01",
  "tsa_url": "https://freetsa.org/tsr",
  "issuer": {
    "name": "EATF.eu",
    "url": "https://eatf.eu",
    "tsps_version": "urn:eatf:tsps:1.0"
  }
}
```

Fields are REQUIRED unless explicitly optional. Implementations MUST
ignore unknown fields (forward-compatibility). The `tenant_id_hash`
intentionally avoids leaking the raw tenant integer; an auditor with the
tenant's secret can verify the binding, an unrelated reader cannot
enumerate tenants.

### 5.1 `agent_id` URN scheme

> **Normative.** Phase 2 v0.1 onwards.

The `agent_id` field carries a tenant-bound URN of the form

```
urn:eatf:tenant:<tenantId>:agent:<slug>
```

where:

- `<tenantId>` is a stable opaque identifier issued by the tenant
  directory (typically a UUID; ≤128 characters).
- `<slug>` is a sanitised, lowercase, dash-separated rendering of the
  agent name. The slug character set is `[a-z0-9-]`; runs of any
  other character collapse to a single dash; leading and trailing
  dashes are trimmed; the slug is bounded to ≤56 characters so that
  an optional disambiguation suffix can be appended without
  exceeding the 64-character agent-portion budget.
- On collision inside a tenant, generators append `-` followed by 8
  hexadecimal characters of entropy.

Legacy identifiers of the form `urn:uuid:<random>` remain valid for
agents registered before this scheme came into force; verifiers MUST
accept both forms. New registrations MUST emit the tenant-bound form
unless no tenant context is available at generation time (e.g.
fixture seeding outside an HTTP request), in which case the legacy
form is permitted as a documented fallback.

The URN binding asserts structural independence: every attested
action visibly names the tenant scope at the identifier level,
without requiring the verifier to consult any external registry.

## 6. Canonicalisation rules

The canonical byte sequence is produced by the following deterministic
algorithm, identified as `eatf-canonical-1`:

1. **Source.** Concatenate, in order: `response.txt` UTF-8 bytes, a
   single LF (`0x0A`) separator, the canonical JSON form of
   `metadata.json` (section 4.4). Implementations MUST NOT include any
   other entries in the canonical bytes.
2. **JSON canonicalisation.** RFC 8785 (JCS):
   - All object members sorted by codepoint of the key.
   - No insignificant whitespace.
   - Numbers serialised per ECMA-404 with no trailing zeros.
   - Strings as JSON strings (escape only what the spec requires).
   - No BOM, UTF-8.
3. **Line endings in `response.txt`.** Preserved verbatim. Implementations
   that perform any normalisation MUST do it BEFORE building the package
   and document the rule in the package's `metadata.canonicalisation`.
4. **The result of step 1 is `canonical.bin`.** It is what the hash and
   the signatures are computed over.

A verifier MUST refuse a package if the recomputed canonical bytes do
not match the embedded `canonical.bin`.

## 7. RFC 3161 timestamp profile

The TSA token is issued over the **hex string** of `hash.sha256`, not
over the raw bytes of `canonical.bin`. The verifier's contract:

1. Decode `timestamp.tsr` from Base64.
2. Parse as a `TimeStampToken` per RFC 3161.
3. Confirm the `messageImprint.hashAlgorithm` is `2.16.840.1.101.3.4.2.1`
   (SHA-256).
4. Confirm `messageImprint.hashedMessage` equals the SHA-256 of the
   ASCII representation of `hash.sha256` (including any trailing newline
   present in the file — recommended to omit).
5. Verify the TSA's signature using the TSA certificate carried in the
   token (or out-of-band trust list — EATF's public TSA cert is
   published at `https://eatf.eu/.well-known/tsa-cert.pem`).

When the issuing TSA is an EATF deployment's local RFC 3161 server,
the genTime is the backend wall clock with a documented drift bound
of ±2 seconds. When the deployment is configured to chain through a
third-party qualified TSA, that TSA's own genTime applies. EATF
itself does not operate as a TSA; the deployment chooses its TSA.

## 8. X.509 certificate profile for signing keys

EATF signing certificates conform to RFC 5280 with:

- Algorithm: `sha256WithRSAEncryption` (1.2.840.113549.1.1.11) for RSA-4096.
- For ML-DSA-65 keys, distribution today is raw PEM (no X.509 wrapping
  pending IETF adoption of ML-DSA OIDs in the LAMPS WG draft); v2 of
  this profile will switch to X.509-wrapped distribution when the LAMPS
  draft stabilises.
- Subject CN: `urn:eatf:signer:<keyId>` where `<keyId>` matches the
  `rsa_key_id` / `pqc_key_id` field in `metadata.json`.
- Validity: rotated annually (Phase 1.10 introduces ceremony automation).
- Extended key usage: `id-kp-codeSigning` plus a custom OID
  `1.3.6.1.4.1.99999.1.1` for "eatf-aep-signing" (placeholder; we will
  request a real OID from IANA as part of the Phase 2 ETSI TR
  submission in step 2.13).

## 9. Ledger entry format

Each evidence package is logged to the per-tenant hash-chained ledger.
The ledger entry is itself signed and timestamped. See
`backend/src/main/java/ai/aletheia/ledger/AletheiaLedgerService.java`
for the canonical implementation. Block fields:

```text
block_index        : long, monotonically increasing per tenant from 0
tenant_id          : UUID/long, scoped lock per Phase 0 step 0.5
previous_hash      : SHA-256 hex of the previous block (genesis = 64 × "0")
merkle_root        : SHA-256 hex of the Merkle root over events in this block
current_hash       : SHA-256 hex over (index ‖ previous_hash ‖ merkle_root ‖ timestamp)
event_count        : integer
created_at         : RFC 3339 timestamp
signing_key_id     : kid present in metadata.rsa_key_id of the signer
signature_pqc      : Base64 ML-DSA-65 signature over the block hash (optional, PQC mode)
```

A verifier rebuilds the chain from index 0 and the embedded keys to
confirm tamper-evidence.

## 10. Versioning

The profile version is recorded in `metadata.schema`. Bump rules:

- **Minor (1.x → 1.y, y > x):** purely additive fields; existing
  verifiers MUST still accept the package.
- **Major (1 → 2):** breaking format change. v2 is planned to (a) make
  PQC entries mandatory, (b) move to X.509-wrapped ML-DSA keys, (c)
  introduce a streaming canonicalisation for >10 MB payloads.

## 11. Conformance levels

A v1 package is **strict conformant** if it includes every REQUIRED
entry, satisfies every canonicalisation rule, and validates against the
verifier reference implementation linked in section 1.

A package is **transitional conformant** if PQC entries are missing
(pre-Phase-1.9 EATF deployments).

A package is **non-conformant** otherwise.

## 12. Reference implementations

- Java (`backend/-Pverifier` shaded JAR): authoritative reference. Maven
  profile `verifier` produces a self-contained JAR with BouncyCastle.
- Python (`sdks/python-sdk/`): planned in Phase 1.20.
- TypeScript / WASM (`sdks/eatf-verifier-ts/`): planned in Phase 1.20.
- Go (`sdks/go-verifier/`): planned in Phase 2 with the agent-economy
  positioning push.

## 13. Test vectors

Authoritative test vectors live at
`backend/src/test/resources/fixtures/`. A v1-conformant verifier MUST
produce expected results on every vector. Vectors include:

- `valid/`: a minimum-form valid package, a PQC-enabled valid package,
  and a maximal-form package with policy_coverage + agent_manifest.
- `tampered/`: packages with each of (hash mismatch, signature
  mismatch, TSA mismatch, metadata field corruption) — verifier MUST
  reject.
- `forward-compat/`: packages with unknown extra metadata fields and
  an unknown extra ZIP entry — verifier MUST accept ignoring them.

## 14. Related documents

- `docs/legal/framework-operations.md` — Framework Operations Statement
  (non-TSP description of how the reference implementation is operated).
- `docs/legal/threat-model.md` — STRIDE threat model.
- `docs/legal/project-sustainability-plan.md` — open-source
  sustainability commitments (replaces the earlier Termination Plan).
- `docs/specs/public-key-mirror.md` — key history.
- ETSI TR submission draft — research draft.

## 15. Changelog

| Version | Date | Notes |
|---|---|---|
| 1.0-draft+overt | 2026-05-14 | Added optional `overt_receipt.json` schema and OVERT-aware verifier obligations. |
| 1.0-draft | 2026-05-12 | Initial Phase 1 step 1.2 draft. Comment period open. |
