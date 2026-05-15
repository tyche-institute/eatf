# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The AEP wire-format profile is versioned separately under its own URN
(`urn:eatf:spec:aep:<major>.<minor>`). A backwards-incompatible
change to the wire format bumps the AEP profile major; a
backwards-incompatible change to the library / CLI surface bumps the
library major.

## [Unreleased]

## [0.1.2] — 2026-05-15

Aligns the v0.1 wire-format documentation and schemas with the
actual AEP layout used by the runnable verifier.

### Added
- **`cli/eatf-inspect/`** — `@eatf/inspect-cli` 0.1.2: pretty-prints
  the structure of an `.aep` package (envelope entries, parsed
  `metadata.json`, parsed `overt_receipt.json`) without verifying
  authenticity. Useful for debugging packaging bugs and inspecting
  received packages before invoking `eatf-verify`. Implemented as a
  thin wrapper around `fflate`.
- **CI** — `schema-validate` job now extracts `metadata.json` from
  every `test-vectors/*/*/package.aep` via `unzip -p` and validates
  it against `schemas/aep-v1.schema.json`. This catches metadata
  drift between the schema and the runtime format.

### Changed
- **`docs/aep-profile.md`** — full v0.1 wire-format specification.
  Replaces the v0.1.0 stub. Documents the eight ZIP entries
  (`canonical.bin`, `hash.sha256`, `metadata.json`,
  `overt_receipt.json`, `public_key.pem`, `response.txt`,
  `signature.sig`, `timestamp.tsr`), the three signature suites
  (`urn:eatf:sig:rsa4096`, `urn:eatf:sig:ecdsa-p256`,
  `urn:eatf:sig:mldsa-65`), and the seven-step verification pipeline.
- **`schemas/aep-v1.schema.json`** — rewritten to describe
  `metadata.json` (the actual content of the AEP that v0.1
  attestations carry), replacing the aspirational manifest schema
  shipped in v0.1.0. The schema now validates against every real
  test-vector metadata file in CI.

## [0.1.1] — 2026-05-15

First release with a runnable offline verifier.

### Added
- **`lib/`** — `@eatf/verifier` 0.1.1 package: full TypeScript
  reference implementation of the EATF offline verifier. Runs in
  Node 20+ and in the browser via Web Crypto.
  - `src/canonical.ts` — RFC 8785 JCS canonicalisation.
  - `src/hash.ts` — SHA-256 over Web Crypto / Node `crypto`.
  - `src/rsa.ts` — RSA-PSS / PKCS#1 v1.5 verification, CMS parsing.
  - `src/mldsa.ts` — ML-DSA-65 (NIST FIPS 204) verification via
    `@noble/post-quantum`.
  - `src/tsa.ts` and `src/tsa-trust-list.ts` — RFC 3161 TimeStampResp
    parsing and TSA trust-anchor management.
  - `src/overt.ts` — OVERT 1.0 receipt validation.
  - `src/verifier.ts` — orchestrates the eight-check verification
    pipeline and returns a structured `VerifyResult`.
  - `src/index.ts` (Node entry) and `src/browser.ts` (Web-Crypto-only
    entry).
- **`cli/eatf-verify/`** — `@eatf/verify-cli` 0.1.1: thin Node CLI
  wrapper over `@eatf/verifier`. Supports single-file verification,
  `--batch <dir>`, `--conformance <vectors-root>`, JSON output, and
  pinned TSA trust lists. No network calls; no API keys.
- **`test-vectors/`** — four real conformance vectors backed by
  `.aep` files:
  - `valid/valid-overt-profile/` — full happy-path, OVERT foundational scope.
  - `valid/mcp-tools-call-valid/` — OVERT `agentic-extended:mcp-tools-call`, policy `allow`.
  - `valid/mcp-tools-call-denied-policy/` — same scope, policy `deny`; the AEP is authentic, the call was rejected.
  - `invalid/tampered-overt-receipt/` — post-sign hash-chain tamper.

### Changed
- **CI** — `schema-validate` job now only compiles the schema (sanity
  check), since the per-vector schema validation of stub manifests no
  longer applies. New `verifier-test` job runs `npm install`,
  `npm run build`, and `vitest` against the verifier. New
  `conformance` job runs the real `eatf-verify --conformance` against
  the four vectors. `hygiene` job unchanged.
- **`docs/aep-profile.md`** previously referenced retired TSP-voice
  artefacts and an internal Java path; updated to point at the
  Framework Operations Statement and to state EATF's eIDAS Article
  3(16) non-trust-service positioning.

### Removed
- `lib/canonicalization/`, `lib/signer/`, `lib/verifier/`,
  `lib/timestamping/`, `lib/package/` placeholder subdirectories —
  replaced by the real `lib/src/*.ts` modules.
- `cli/eatf-sign/`, `cli/eatf-inspect/` placeholder directories — the
  signing CLI lands in a later 0.1.x; the inspect CLI is folded into
  `eatf-verify --json` for now.
- `cli/eatf-verify/eatf-verify` Bash stub — superseded by the real
  Node CLI under `cli/eatf-verify/bin/eatf-verify.js`.
- `test-vectors/valid/01-minimal-stub/` and
  `test-vectors/invalid/01-tampered-record-stub/` manifest-only stub
  vectors — superseded by real `.aep` files.

## [0.1.0] — 2026-05-14

Initial public release of the project scaffold.

### Added
- Apache License 2.0.
- `NOTICE` declaring the standards-relationship classification and
  the project's positioning relative to eIDAS.
- `README.md` with the "what EATF is / what EATF is NOT" framing.
- `CONTRIBUTING.md` using the Developer Certificate of Origin (DCO);
  no CLA.
- `CODE_OF_CONDUCT.md` based on Contributor Covenant 2.1.
- `SECURITY.md` with a coordinated-disclosure policy and a triage SLA.
- Top-level directory layout: `docs/`, `schemas/`, `lib/`, `cli/`,
  `examples/`, `test-vectors/`, `.github/`.

### Notes

This 0.1.0 release deliberately shipped specifications and
scaffolding before runnable code. v0.1.1 replaces the lib/ and
cli/eatf-verify/ scaffolding with the real implementation.

[Unreleased]: https://github.com/tyche-institute/eatf/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.2
[0.1.1]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.1
[0.1.0]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.0
