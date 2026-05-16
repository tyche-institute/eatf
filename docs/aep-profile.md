# Agent Evidence Package (AEP) — wire-format profile

**Status:** v0.1 (2026-05-15). Subject to revision; backwards-
incompatible changes bump the profile URN major.

**Profile URN:** `urn:eatf:spec:aep:1.0`

EATF is not a trust service under eIDAS Article 3(16); the format
documented here is a technical self-attestation envelope, not a
Qualified Electronic Attestation of Attributes (QEAA) under Article
3(45). The verifier in [`lib/`](../lib/) implements this profile and
is the executable source of truth alongside this document.

## Goal

The AEP is a self-contained, offline-verifiable artefact that
documents an agent's action. A verifier with no network access and
no API keys must be able to assess the package's authenticity,
integrity, and timeliness from the artefact alone, given only:

1. The `.aep` file.
2. (Optionally) one or more trust anchors for the RFC 3161
   timestamping authority that signed the embedded timestamp token.

The issuer public key is carried inside the package itself
(`public_key.pem`). Trust in that key is configured by the verifier
(typically pinned to a key-history mirror; see
[`docs/specs/public-key-mirror.md`](specs/public-key-mirror.md) for
the deployment-managed scheme).

## Envelope

An AEP is a ZIP archive with a **flat** internal layout:

```
package.aep/
├── canonical.bin       RFC 8785 JCS canonicalisation of the signed
│                       JSON payload (the bytes over which the
│                       signature is computed).
├── hash.sha256         Hex SHA-256 of canonical.bin. Allows a
│                       verifier to confirm the canonicalisation
│                       without re-running JCS, and acts as the
│                       value timestamped by the TSA.
├── metadata.json       Attestation metadata — attestation_id,
│                       agent_id, action_type, policy fields,
│                       created_at, format_version. Schema:
│                       schemas/aep-v1.schema.json.
├── overt_receipt.json  OVERT 1.0 receipt: scope, subject, policy,
│                       content_hash, witness pointers. Always
│                       present in v0.1.
├── public_key.pem      Issuer public key (PEM). Used by the
│                       verifier to validate signature.sig.
├── response.txt        Original payload being attested (e.g. the
│                       agent's response, the MCP tool result).
│                       When metadata.privacy_mode is true,
│                       response.txt MAY be omitted and the OVERT
│                       receipt's content_hash is the only binding
│                       to the payload.
├── signature.sig       Classical signature over canonical.bin,
│                       base64-encoded (ASCII + LF). v0.1 suite:
│                       RSASSA-PKCS1-v1_5 with SHA-256, using the
│                       key in public_key.pem.
├── signature_pqc.sig   OPTIONAL ML-DSA-65 (NIST FIPS 204)
│                       signature over canonical.bin, base64-
│                       encoded. Producers SHOULD include it for
│                       forward-compatibility against quantum
│                       attacks; verifiers MUST validate it when
│                       present (paired with pqc_public_key.pem).
├── pqc_public_key.pem  OPTIONAL ML-DSA-65 public key (PEM-like
│                       envelope around the FIPS 204 raw public
│                       key). Required when signature_pqc.sig is
│                       present.
└── timestamp.tsr       RFC 3161 TimeStampResp. The timestamped
                        value SHOULD be the SHA-256 in hash.sha256;
                        verifiers accept legacy packages where the
                        imprint differs but the SignerInfo signature
                        still verifies against the embedded
                        certificate.
```

The ZIP layout is deterministic: entries are stored in sorted path
order, per-entry timestamps are fixed to the AEP protocol epoch
(`1980-01-01T00:00:00Z`), and the compression mode is `STORED`. The
central directory ordering matches the local-file-header ordering.

## Canonicalisation

`canonical.bin` is produced by serialising the source object as JSON
and then normalising the bytes per [RFC 8785 JSON Canonicalization
Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785.html). The
canonical form is what gets signed and timestamped; any
non-canonical JSON serialisation MUST NOT be used as input to
verification.

The reference JCS implementation lives at
[`lib/src/canonical.ts`](../lib/src/canonical.ts).

## Hashing

All hash operations in v0.1 use **SHA-256**. The hex form is
lower-case, 64 characters. The value in `hash.sha256` MUST equal
`SHA-256(canonical.bin)`.

## Signature suites

v0.1 defines two suite identifiers:

| Suite identifier              | Algorithm                                       | Signature entry      |
|-------------------------------|-------------------------------------------------|----------------------|
| `urn:eatf:sig:rsa4096`        | RSASSA-PKCS1-v1_5 with SHA-256, 4096-bit modulus| `signature.sig`      |
| `urn:eatf:sig:mldsa-65`       | ML-DSA-65 (NIST FIPS 204 / Dilithium3)          | `signature_pqc.sig`  |

A v0.1 package carries at least one classical signature (RSA-PSS or
ECDSA-P256) in `signature.sig` and SHOULD carry an ML-DSA-65 signature
in `signature.mldsa`. Verifiers MUST validate the classical signature
in `signature.sig` and MUST also validate `signature.mldsa` when
present.

The classical and post-quantum signatures cover **exactly** the bytes
of `canonical.bin`. No additional pre-hashing or framing.

## Timestamping

`timestamp.tsr` is an RFC 3161 `TimeStampResp` produced by a TSA
chosen by the deployment operator. The message imprint inside the
token MUST equal SHA-256 of `canonical.bin` (i.e. the value in
`hash.sha256`).

EATF itself does not operate as a TSA. Each deployment chooses its
own TSA; the trust list for verification is supplied by the
verifier's caller. The library ships a default trust list that
recognises several public TSA providers; see
[`lib/src/tsa-trust-list.ts`](../lib/src/tsa-trust-list.ts).

## OVERT receipt

`overt_receipt.json` is an OVERT 1.0 receipt with the following
required fields:

```json
{
  "overt": "1.0.0",
  "profile": "urn:eatf:spec:aep:1.0",
  "profile_revision": "1.0-draft",
  "scope": "<scope-urn>",
  "subject": { "agent_id": "...", "tenant_hash": "...", "system": "...", "revision": "..." },
  "event":   { "type": "...", "timestamp": "...", "action_type": "..." },
  "policy":  { "id": "...", "version": "...", "coverage": <float>, "decision": "allow|deny|warn|abstain" },
  "content_hash": "sha256:<hex>",
  "prev": "<aep-id-or-null>",
  "witness": { "iap": "EATF.eu", "signature_refs": ["signature.sig"], "timestamp_refs": ["timestamp.tsr"] }
}
```

The `content_hash` field MUST equal `sha256:` followed by SHA-256 of
`canonical.bin` (lower-case hex). The verifier in
[`lib/src/overt.ts`](../lib/src/overt.ts) cross-checks this.

In v0.1 the OVERT scope is one of:

- `foundational:aep-response` — base scope; any signed agent response.
- `agentic-extended:mcp-tools-call` — MCP `tools/call` attestation.

## Verification pipeline

A v0.1-conformant verifier MUST perform the following checks, in this
order, before reporting `verify=true`:

1. **Envelope.** Package is a well-formed ZIP and contains the seven
   mandatory entries (`canonical.bin`, `hash.sha256`,
   `metadata.json`, `overt_receipt.json`, `public_key.pem`,
   `signature.sig`, `timestamp.tsr`). `response.txt` is mandatory
   unless `metadata.privacy_mode == true`. `signature.mldsa` is
   optional.
2. **Canonicalisation.** `hash.sha256` matches `SHA-256(canonical.bin)`.
3. **Classical signature.** `signature.sig` verifies against
   `public_key.pem` over `canonical.bin`.
4. **Post-quantum signature.** If `signature.mldsa` is present, it
   verifies against the ML-DSA-65 public key for the same issuer
   over `canonical.bin`.
5. **Timestamp.** `timestamp.tsr` is a valid RFC 3161 response whose
   message imprint equals SHA-256 of `canonical.bin`, and whose TSA
   signing certificate validates against the verifier's configured
   trust list (when one was supplied).
6. **OVERT receipt.** `overt_receipt.json` parses, `overt == "1.0.0"`,
   `profile == "urn:eatf:spec:aep:1.0"`, and
   `content_hash == "sha256:" + SHA-256(canonical.bin)`.
7. **Metadata.** `metadata.json` validates against
   `schemas/aep-v1.schema.json`.

The reference implementation runs these checks in
[`lib/src/verifier.ts`](../lib/src/verifier.ts).

## Non-goals

- AEP is **not** a Qualified Electronic Attestation of Attributes
  (QEAA) under eIDAS Article 3(45). It is a technical
  self-attestation by the deployment operator.
- AEP is **not** a substitute for an audit log written to durable
  storage by the operator. It is a portable receipt that complements
  such logs, not a replacement.
- AEP v0.1 does not standardise the semantics of what an agent's
  action records describe; the OVERT receipt's `scope` and the
  `metadata.action_type` field name the action class, but the
  semantics of any given class are out of scope for this profile.

## Related documents

- [`docs/architecture.md`](architecture.md) — layered overview.
- [`docs/threat-model.md`](threat-model.md) — STRIDE analysis.
- [`docs/design-rationale.md`](design-rationale.md) — why offline
  verification, why hybrid signing, why private CA.
- [`docs/glossary.md`](glossary.md) — AEP, JCS, JCS, ML-DSA, OVERT,
  TSA, VC.
- [`schemas/aep-v1.schema.json`](../schemas/aep-v1.schema.json) — JSON
  Schema 2020-12 for `metadata.json`.
- [`test-vectors/`](../test-vectors/) — conformance vectors.
