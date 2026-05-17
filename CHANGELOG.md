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

## [0.1.5] — 2026-05-17

Documentation and schema completeness. Fills in every `docs/`
stub that has been carrying a placeholder since v0.1.0, and adds
a second JSON Schema covering the OVERT receipt that the verifier
already validates structurally.

### Added
- **`schemas/overt-receipt-v1.schema.json`** — JSON Schema
  2020-12 for the `overt_receipt.json` entry. Constrains the
  receipt's shape; cross-document consistency between receipt and
  manifest is enforced by the verifier itself
  (`lib/src/overt.ts`). Validated against all 11 conformance
  vectors as part of CI.
- **`docs/architecture.md`** (~280 lines, previously stub) —
  full layered overview, per-layer responsibilities, mapping to
  `lib/src/*` modules, trust boundaries, cryptographic-primitives
  summary table.
- **`docs/threat-model.md`** (~180 lines) — focused STRIDE
  analysis mapped to the eight verifier checks, eleven-row
  threat table, residual-risks section, future-hardening list.
- **`docs/attestation-profile.md`** (~190 lines) — W3C VC 2.0
  profile for the planned `attestations/agent.vc.json` entry,
  private-CA-default + external-issuer-bound modes, cross-document
  consistency rules, explicit non-implementation marker for v0.1.
- **`docs/glossary.md`** (~180 lines) — EATF-specific terms,
  standards-relationship labels (IMPLEMENTED / ALIGNED /
  REFERENCED / ADDRESSED), implementation-maturity labels,
  cryptographic-primitives definitions, regulatory references
  (EU AI Act, eIDAS, GDPR).
- **`docs/design-rationale.md`** (~230 lines) — the *why* behind
  each major design decision: offline verification, hybrid
  signing, RSASSA-PKCS1-v1_5 default, ML-DSA-65 selection, JCS
  canonicalisation, RFC 3161 timestamps, private CA for agents,
  open specification, DCO over CLA, no hosted registry.

### Changed
- **CI `schema-validate` job** now compiles both schemas (AEP
  metadata + OVERT receipt) and validates the corresponding
  document extracted from every conformance vector. Catches any
  drift between the schemas and the runtime format.

## [0.1.4] — 2026-05-17

Failure-mode coverage. Six new invalid conformance vectors that
exercise the six classes of tamper a v0.1-conformant verifier
must catch.

### Added
- **`test-vectors/invalid/tampered-canonical-bin/`** — one byte
  flipped in `canonical.bin`; hash chain mismatch.
- **`test-vectors/invalid/tampered-metadata/`** —
  `metadata.policy_decision` swapped; OVERT receipt cross-check
  fails.
- **`test-vectors/invalid/bad-signature-classical/`** — one byte
  flipped inside the base64-decoded `signature.sig`;
  RSASSA-PKCS1-v1_5 verification fails.
- **`test-vectors/invalid/untrusted-issuer/`** — `public_key.pem`
  swapped for a freshly-generated unrelated RSA-4096 public key;
  the original signature does not verify against the swap.
- **`test-vectors/invalid/missing-canonical-bin/`** — required
  envelope entry deleted; verifier fails the envelope-integrity
  check before any cryptographic step.
- **`test-vectors/invalid/bad-timestamp/`** — three bytes flipped
  inside `timestamp.tsr`; pkijs cannot extract a usable TimeStampToken,
  verifier reports "timestamp.tsr missing or empty".
- **`scripts/generate-invalid-vectors.mjs`** — deterministic
  build-time generator that produces all six tampered packages
  from `valid/minimal-roundtrip/package.aep`. Re-running produces
  byte-identical output. Inspect this script to audit exactly
  what each tamper does.
- **`scripts/package.json`** — minimal manifest pinning `fflate`
  so the generator runs from a clean clone without depending on
  `lib/node_modules`.
- **`test-vectors/README.md`** — table of all eleven vectors
  (4 valid + 7 invalid), expected output of a full conformance run.

### Changed
- Conformance contract now requires verifiers to handle six new
  failure modes correctly. Output of
  `eatf-verify --conformance test-vectors/` goes from
  `4 verified, 1 rejected, 0 contract mismatches` →
  `4 verified, 7 rejected, 0 contract mismatches`.

### Coming next
- `tyche-institute/verify-aep-action@v1` — a sibling repository
  shipping a GitHub composite Action that wraps `eatf-verify`,
  for downstream pipelines that want to assert every `.aep` they
  produce verifies cleanly before merging.
- v0.1.5 — OVERT receipt JSON Schema + fill in the remaining
  `docs/` stubs.

## [0.1.3] — 2026-05-15

First release with a runnable offline signer. Closes the round-trip
loop: external parties can now both verify and produce `.aep`
packages from the public repository alone.

### Added
- **`lib/src/signer.ts`** — `sign()` function added to `@eatf/verifier`.
  Takes a payload + RSA keypair + metadata + OVERT scope + RFC 3161
  timestamp token, returns a v0.1-conformant `.aep` ZIP. Uses the
  Java-form canonical bytes (`canonical.bin == response.txt`) and
  RSASSA-PKCS1-v1_5 over SHA-256, matching the verifier's
  expectation exactly.
- **`cli/eatf-sign/`** — `@eatf/sign-cli` 0.1.3: thin Node CLI
  wrapper over `sign()`. Supports `--gen-rsa` for one-off dev
  keypair generation, and a `--timestamp <path.aep>:timestamp.tsr`
  shorthand for reusing an RFC 3161 token from an existing package
  (the offline-by-default option). No network calls; the signer
  does not contact any TSA.
- **`test-vectors/keys/dev-rsa-4096.{key,pem}`** — public-and-
  private development RSA keypair, checked into the repo
  intentionally so that anyone can regenerate the round-trip
  vector and confirm byte-equality. README explicitly marks the
  key as a known-bad anchor for production verifiers.
- **`test-vectors/valid/minimal-roundtrip/`** — produced by
  `eatf-sign` from `dev-rsa-4096.key`, verifies clean with
  `eatf-verify`. Reuses the RFC 3161 token from
  `valid-overt-profile/` (verifier accepts mismatched-imprint
  timestamps as long as the SignerInfo signature still verifies
  against the embedded certificate).
- **CI** — new `roundtrip` job. Builds the verifier, builds the
  signer CLI, signs a fixture payload with the dev key, runs the
  verifier on the result, asserts `verify=true`. Catches any
  regression that breaks signer↔verifier agreement.

### Changed
- **`docs/aep-profile.md`** — wire-format spec now matches the
  verifier and signer reality:
  - Classical suite identified as RSASSA-PKCS1-v1_5 + SHA-256 (the
    v0.1.2 doc incorrectly said RSA-PSS).
  - Post-quantum signature entry renamed to `signature_pqc.sig`
    (paired with `pqc_public_key.pem`) — matches the verifier
    code. The v0.1.2 doc incorrectly said `signature.mldsa`.
  - Timestamp section notes that legacy packages with mismatched
    imprints are still accepted as long as the SignerInfo signature
    verifies against its embedded certificate.
- **`lib/package.json`** version bumped to `0.1.3`. The
  `@eatf/verifier` package now exports both `verify` and `sign`.

### Not yet in this release
- ML-DSA-65 signing in `eatf-sign` (verifier already handles
  packages that carry it; signer support lands next).
- Six tampered failure-mode vectors (v0.1.4).
- OVERT receipt JSON Schema (v0.1.5).
- Expanded `docs/` spec pages (v0.1.5).

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

[Unreleased]: https://github.com/tyche-institute/eatf/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.5
[0.1.4]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.4
[0.1.3]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.3
[0.1.2]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.2
[0.1.1]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.1
[0.1.0]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.0
