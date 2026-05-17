# EATF architecture

**Status:** v0.1 (2026-05-17). Stable. Subsequent revisions of the
architecture follow the same `urn:eatf:spec:aep:<major>.<minor>`
versioning rule as the wire format.

This document describes the layered structure of the EATF reference
implementation in this repository (`lib/` + `cli/`). It is the
companion to [`docs/aep-profile.md`](aep-profile.md) (the wire format)
and [`docs/threat-model.md`](threat-model.md) (what each layer
defends against).

EATF is not a trust service under eIDAS Article 3(16). The layers
below name technical responsibilities; they do not name eIDAS legal
roles. Operators deploying EATF take any legal trust-service
positioning at their own boundary; EATF the framework intentionally
stays out of that.

## Layered overview

```
Layer 7 — Reference deployments and downstream integrations
          (NOT in this repository — independent operators)
─────────────────────────────────────────────────────────────────
Layer 6 — Verifier orchestration                              lib/src/verifier.ts
Layer 5 — Package envelope (deterministic ZIP, AEP layout)    lib/src/canonical.ts (envelope side)
Layer 4 — Timestamp (RFC 3161 client + TSA trust list)        lib/src/tsa.ts, tsa-trust-list.ts
Layer 3 — Signature suites (RSA-PSS, ECDSA-P256, ML-DSA-65)    lib/src/rsa.ts, mldsa.ts
Layer 2 — Canonicalisation (RFC 8785 JCS) + hashing (SHA-256)  lib/src/canonical.ts, hash.ts
Layer 1 — Standards EATF relates to                            ../docs/aep-profile.md, ../docs/glossary.md
```

The verifier in `lib/src/verifier.ts` walks the package from Layer 5
down to Layer 2, then back up through Layer 3 (signature
verification), Layer 4 (timestamp validation), and finally cross-
references the OVERT 1.0 receipt against the manifest. Each layer is
independently testable; the conformance vectors in `test-vectors/`
each target a specific layer's failure modes (see
[`test-vectors/README.md`](../test-vectors/README.md)).

## Standards-relationship legend

Every component the project relates to a standard receives one of
four labels. The labels distinguish *technical implementation* from
*regulatory conformance* — neither label implies the other.

- **IMPLEMENTED** — the reference implementation in `lib/` realises
  the standard end-to-end and is covered by test vectors in
  `test-vectors/`. Example: RFC 8785 JCS, implemented in
  `lib/src/canonical.ts`, exercised by every signed package.
- **ALIGNED** — the reference implementation follows the standard's
  required structures and semantics but has not been independently
  conformance-tested. Example: RFC 3161 timestamps — the format is
  followed, the SignerInfo signature is verified, but the TSA chain-
  to-trusted-root check is operator-configurable rather than
  exhaustively tested.
- **REFERENCED** — the standard is cited for design vocabulary or
  policy reasoning; this project does not claim to implement it.
  Examples: ETSI EN 319 401 (applies to TSPs; EATF is not a TSP),
  RFC 3647 (CP/CPS framework; we publish a Framework Operations
  Statement instead).
- **ADDRESSED** — a regulatory or policy reference; the project
  documents how the regulation bears on EATF's positioning but does
  not itself fulfil the regulation. Examples: EU AI Act Articles 12,
  14, 50; eIDAS Article 3(16) — addressed via NOTICE + this
  document's positioning statement.

Implementation-maturity labels (`IMPLEMENTED` aside) on the
public-site architecture diagram —
`PRODUCTION` / `WORKING` / `PARTIAL` / `PROTOTYPE` / `STUB` /
`PLANNED` — describe the state of a given module in this reference
implementation. They are orthogonal to standards-relationship
labels: a component can be `IMPLEMENTED`-relative-to-a-standard
while still being `PROTOTYPE`-mature.

## Layer-by-layer

### Layer 2 — Canonicalisation and hashing

[`lib/src/canonical.ts`](../lib/src/canonical.ts) and
[`lib/src/hash.ts`](../lib/src/hash.ts).

**Canonicalisation:** RFC 8785 JSON Canonicalization Scheme (JCS).
Every JSON document signed by EATF is normalised to JCS bytes before
hashing. Sorting is lexicographic by codepoint of the key; no
insignificant whitespace; numbers per ECMA-404 with no trailing
zeros; strings JSON-escaped per RFC 8259.

**Hash function:** SHA-256 (FIPS 180-4) for both `canonical.bin`
content addressing and the RFC 3161 message imprint. Hex output is
lower-case, 64 characters.

**ZIP envelope:** deterministic layout. Entries sorted lexicographically;
per-entry timestamps fixed to the AEP protocol epoch (`1980-01-01T00:00:00Z`);
compression `STORED`; central-directory order matches local-file-header
order. The reference signer in [`lib/src/signer.ts`](../lib/src/signer.ts)
emits packages that re-zip byte-identically.

### Layer 3 — Signature suites

[`lib/src/rsa.ts`](../lib/src/rsa.ts) and
[`lib/src/mldsa.ts`](../lib/src/mldsa.ts).

Three suites are defined; a v0.1-conformant package carries at least
one classical signature (RSA-PSS-SHA256 or ECDSA-P256) and SHOULD
carry an ML-DSA-65 post-quantum signature side-by-side.

| Suite identifier              | Algorithm                                       | Signature entry      |
|-------------------------------|-------------------------------------------------|----------------------|
| `urn:eatf:sig:rsa4096`        | RSASSA-PKCS1-v1_5 with SHA-256, 4096-bit modulus| `signature.sig`      |
| `urn:eatf:sig:ecdsa-p256`     | ECDSA over P-256 with SHA-256                   | `signature.sig`      |
| `urn:eatf:sig:mldsa-65`       | ML-DSA-65 (NIST FIPS 204 / Dilithium3)          | `signature_pqc.sig`  |

Verifiers MUST validate the classical signature and, when present,
MUST also validate the ML-DSA-65 signature. Both signatures cover
the same `canonical.bin` bytes verbatim.

Web Crypto's `RSASSA-PKCS1-v1_5` path is the primary verification;
the verifier falls back to a hand-written DigestInfo path
(`verifyRsaDigestInfo`) for compatibility with the Java reference
implementation's signature shape.

### Layer 4 — Timestamping

[`lib/src/tsa.ts`](../lib/src/tsa.ts) and
[`lib/src/tsa-trust-list.ts`](../lib/src/tsa-trust-list.ts).

RFC 3161 client + parser. The verifier:

1. Decodes `timestamp.tsr` from base64 (or accepts raw DER).
2. Parses as `TimeStampToken` using pkijs.
3. Confirms the `messageImprint.hashAlgorithm` is SHA-256 (OID
   `2.16.840.1.101.3.4.2.1`).
4. Confirms `messageImprint.hashedMessage` equals SHA-256 of the
   ASCII representation of `hash.sha256`.
5. Verifies the TSA's SignerInfo signature using the TSA certificate
   carried inside the token.
6. Optionally validates the TSA certificate chain against the
   verifier's configured TSA trust list
   (`DEFAULT_TSA_TRUST_LIST` ships three pinned DigiCert public TSA
   roots; callers can substitute their own or pass `tsaTrustList: []`
   to skip the check).

EATF itself does not operate a TSA. Each deployment chooses an
RFC 3161-compliant TSA — local, public (e.g. freetsa.org), or
operator-contracted qualified.

### Layer 5 — Package envelope

The package envelope is the flat ZIP described in
[`docs/aep-profile.md`](aep-profile.md) §3 — eight required entries
plus optional PQC entries plus the OVERT receipt. Layer 5 is the
boundary the verifier crosses first: open the ZIP, enumerate
entries, fail fast if any required entry is missing.

### Layer 6 — Verifier orchestration

[`lib/src/verifier.ts`](../lib/src/verifier.ts) is the entry point:

```ts
export async function verify(
  input: Uint8Array | ArrayBuffer | Blob,
  opts: VerifyOptions = {},
): Promise<VerifyResult>
```

Pipeline (each step short-circuits on failure):

1. Unzip the package.
2. Confirm required entries are present.
3. Parse `metadata.json`.
4. Re-derive canonical bytes; compare to embedded `canonical.bin`.
5. Hash `canonical.bin`; compare to `hash.sha256`.
6. Verify RSA signature against `public_key.pem`.
7. Parse + validate the OVERT receipt against `metadata.json` +
   the hash from step 5.
8. If present, verify the ML-DSA-65 signature against
   `pqc_public_key.pem`.
9. Parse RFC 3161 timestamp; verify SignerInfo signature; optionally
   chain-to-root against the configured TSA trust list.

The return type carries the boolean `valid`, a structured
`failureReason` on failure, a list of `report` lines for telemetry,
and decoded `metadata` + `overtReceipt` so the caller can render
human-meaningful output without re-parsing the package.

### Layer 7 — Reference deployments and downstream integrations

Out of repository scope. Reference deployments
([h2oatlas.ee](https://h2oatlas.ee), [matx.ee](https://matx.ee),
[eaudit.ee](https://eaudit.ee)) are run by independent community
operators and are not part of `lib/`, `cli/`, or any test surface
here. They appear in `Layer 7` of the public-site architecture
diagram for context only.

Downstream integrators MAY:

- Embed `@eatf/verifier` directly in a browser or Node application.
- Wrap the CLI with [`tyche-institute/verify-aep-action@v1`](https://github.com/tyche-institute/verify-aep-action)
  to run conformance checks inside their own CI pipelines.
- Implement an independent verifier in any language and validate
  against `test-vectors/` (see [`docs/glossary.md`](glossary.md) for
  the conformance contract).

## Trust boundaries

The verifier is a pure function of:

- The package bytes (`Uint8Array`).
- The caller-supplied options (`tsaTrustList`, `offlineOnly`).

It does not perform network I/O, does not read environment variables,
and does not write to disk. The only state crossing the boundary is
the caller-supplied trust list, which is a configuration decision the
deployment makes, not a framework feature.

Three boundary categories outside the verifier's enforcement:

1. **Operator key custody.** The signer's private key never enters
   the verifier. The verifier trusts whoever signed `canonical.bin`
   exactly to the extent the caller's trust anchors say so.
2. **TSA trust.** The verifier validates the TSA SignerInfo
   signature; whether the TSA's root is trustworthy is determined by
   the caller's `tsaTrustList`.
3. **Transport security.** The verifier sees a `Uint8Array`. How the
   package got from signer to verifier (HTTPS, S3, USB drive, email)
   is the operator's concern.

## Cryptographic primitives summary

| Primitive                    | Algorithm                            | Library                          | Standard          |
|------------------------------|--------------------------------------|----------------------------------|-------------------|
| Hash                         | SHA-256                              | Web Crypto / Node `crypto`       | FIPS 180-4        |
| Canonical JSON               | JCS                                  | `lib/src/canonical.ts`           | RFC 8785          |
| RSA verification (primary)   | RSASSA-PKCS1-v1_5 + SHA-256          | Web Crypto                       | RFC 8017          |
| RSA verification (fallback)  | DigestInfo manual unwrap             | `lib/src/rsa.ts`                 | RFC 8017          |
| ECDSA verification           | P-256 + SHA-256                      | Web Crypto                       | FIPS 186-5        |
| Post-quantum signature       | ML-DSA-65 (Dilithium3)               | `@noble/post-quantum`            | NIST FIPS 204     |
| RFC 3161 timestamp parsing   | ASN.1 TimeStampToken                 | `pkijs`, `asn1js`                | RFC 3161          |
| X.509 cert chain             | RFC 5280 path validation             | `pkijs`                          | RFC 5280          |
| ZIP envelope                 | PKZIP, STORED, deterministic order   | `fflate`                         | APPNOTE 6.3.x     |

## Related documents

- [`aep-profile.md`](aep-profile.md) — wire-format specification.
- [`attestation-profile.md`](attestation-profile.md) — W3C VC profile
  for the optional `attestations/agent.vc.json` entry.
- [`threat-model.md`](threat-model.md) — STRIDE analysis mapped to
  each verifier check.
- [`design-rationale.md`](design-rationale.md) — why offline
  verification, why hybrid signing, why no registry.
- [`glossary.md`](glossary.md) — terminology and standards labels.
