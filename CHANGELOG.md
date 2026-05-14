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

### Added
- Documentation stubs in `docs/` (architecture, AEP profile,
  attestation profile, threat model, design rationale, glossary).
- Subdirectory placeholders for the reference implementation
  (`lib/canonicalization`, `lib/signer`, `lib/verifier`,
  `lib/timestamping`, `lib/package`), the CLI (`cli/eatf-sign`,
  `cli/eatf-verify`, `cli/eatf-inspect`), examples
  (`examples/01-minimal-sign-and-verify` …
  `examples/04-private-ca-setup`), schemas, and test vectors. The
  working implementation is being ported from the internal research
  codebase and will land in successive 0.1.x point releases.

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

This 0.1.0 release deliberately ships specifications and scaffolding
before runnable code. The cryptographic primitives, signer, verifier,
and AEP packaging layer are documented here in stub form; the working
implementation will be ported from the internal research codebase in
0.1.x point releases. Pinning to 0.1.0 today gives early integrators
a stable reference point for the project's positioning, license, and
governance even before the reference code lands.

[Unreleased]: https://github.com/tyche-institute/eatf/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tyche-institute/eatf/releases/tag/v0.1.0
