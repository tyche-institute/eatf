# EATF documentation

This directory contains the canonical EATF specifications and reference
documents. Each file is normative for the v0.1 line unless explicitly
marked as informational.

| File                          | Status      | Summary                                                                                       |
|-------------------------------|-------------|-----------------------------------------------------------------------------------------------|
| `architecture.md`             | stub        | Layered overview of the reference implementation and the standards-relationship legend.       |
| `aep-profile.md`              | stub        | Agent Evidence Package wire format: ZIP layout, JCS canonicalisation, hybrid signing.         |
| `attestation-profile.md`      | stub        | Agent attestation record format and signing modes.                                            |
| `threat-model.md`             | stub        | STRIDE-style trust boundaries, residual risks, planned mitigations.                           |
| `design-rationale.md`         | stub        | Why offline verification, why hybrid signing, why private CA, why open spec.                  |
| `glossary.md`                 | stub        | Definitions for AEP, VC, TSA and the IMPLEMENTED/ALIGNED/REFERENCED/ADDRESSED label set.      |

**Status legend** (matches the public site at /standards):

- `IMPLEMENTED` — the reference implementation in `lib/` realises the
  standard end-to-end and is covered by test vectors in `test-vectors/`.
- `ALIGNED` — the reference implementation follows the standard's
  required structures and semantics but has not been independently
  conformance-tested.
- `REFERENCED` — the standard is cited for design or vocabulary; this
  project does not claim to implement it.
- `ADDRESSED` — the standard is a regulatory or policy reference; the
  project documents how it bears on EATF's positioning but does not
  itself fulfil the standard.

The "stub" status above applies to the documents themselves: the
v0.1.0 public release ships the directory layout, project framing and
license, and a placeholder for each canonical document. Filled-in
specifications will land in successive 0.1.x point releases.

## Conventions

- All documents are CommonMark with [GFM tables](https://github.github.com/gfm/).
- Wire-format diagrams use [Mermaid](https://mermaid.js.org/).
- Cryptographic notation follows IETF style: `H(x)` for hashes,
  `Sig(k, m)` for signatures, `||` for concatenation. Where the IETF
  and W3C terminologies diverge (e.g. "proof" vs "signature"), the
  W3C VC spelling is used inside VC contexts and the IETF spelling
  elsewhere, with an explicit cross-reference in `glossary.md`.
