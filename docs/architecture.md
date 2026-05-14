# EATF architecture (stub)

**Status:** stub for v0.1.0. The full architectural document, including
Mermaid diagrams, lands in a 0.1.x point release.

## Layers

The reference implementation is organised in seven layers. Layers 1–6
are library/CLI concerns and live in this repository under `lib/` and
`cli/`. Layer 7 (reference deployments) is operated independently by
community contributors and is **not** included here.

| Layer | Name                      | Responsibility                                                                                | Status        |
|-------|---------------------------|-----------------------------------------------------------------------------------------------|---------------|
| 1     | Standards                 | Cryptographic and policy standards the project relates to (RFC 3161, RFC 8785, FIPS 204, …). | REFERENCED    |
| 2     | Canonicalisation          | RFC 8785 JCS for JSON; deterministic ZIP layout for the package envelope.                     | stub          |
| 3     | Signer                    | Hybrid signing: RSA-4096 (or ECDSA-P256) + ML-DSA-65, side-by-side detached signatures.       | stub          |
| 4     | Timestamping              | RFC 3161 client for binding manifest signatures to a trusted-third-party timestamp.           | stub          |
| 5     | Package                   | AEP ZIP envelope construction, content-addressed hashing, attestation embedding.              | stub          |
| 6     | Verifier                  | Offline verifier: signature, hash chain, timestamp, trust-anchor validation.                  | stub          |
| 7     | Reference deployments     | Independent operator deployments (h2oatlas.ee, matx.ee, eaudit.ee). Out of repository scope.  | REFERENCED    |

## Standards-relationship legend

This project uses four labels, matching the public site at /standards:

- **IMPLEMENTED** — realised end-to-end in `lib/` and covered by test
  vectors in `test-vectors/`.
- **ALIGNED** — follows the standard's required structures and
  semantics; not independently conformance-tested.
- **REFERENCED** — cited for design or vocabulary; this project does
  not claim to implement it.
- **ADDRESSED** — a regulatory or policy reference; the project
  documents how the standard bears on its positioning but does not
  itself fulfil the standard.

Implementation-maturity labels (PRODUCTION / WORKING / PARTIAL /
PROTOTYPE / STUB / PLANNED) are an orthogonal axis describing the
state of a given component in the reference implementation. The
two label sets are kept distinct: a component can be IMPLEMENTED-aligned
to a standard while still being PARTIAL in maturity.

## Trust boundaries

- **Operator key custody** lies outside the repository. The reference
  implementation accepts keys from the filesystem, a PKCS#11 token,
  or a process-local environment variable; it does not provide a
  hosted key-management service.
- **Trust anchors** (issuer-CA roots, TSA roots) are configuration
  inputs. The repository ships test trust anchors under
  `test-vectors/` but does not bundle production anchors.
- **Verifiers** trust their configured anchor set and the package's
  internal hash chain. They do not trust the package's filename, ZIP
  comment, or any non-signed metadata.

See [`threat-model.md`](./threat-model.md) for the full STRIDE
analysis.
