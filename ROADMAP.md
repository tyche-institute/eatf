# Roadmap

This document describes the planned trajectory of the EATF public
repository. Versions are not deadlines — they are an ordering of
work by priority and dependency. Each item is voluntary; community
contributions of any of them are welcome.

See [`CHANGELOG.md`](./CHANGELOG.md) for what has shipped.
See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for what we will and
will not accept.

## Scope reminder

**In scope (commodity):** spec, schemas, conformance vectors,
verifier libraries in multiple languages, sign-and-inspect CLIs,
testing tools for downstream integrators.

**Out of scope (deliberate):** Tyche Institute's reference
deployment infrastructure (backend, frontend, ops, deployment
pipelines, tenant management, billing, customer onboarding). EATF
the framework is open; eatf.eu the operating deployment is a
private product. Same pattern as Let's Encrypt / Boulder vs. ISRG
operations, or ACME RFC vs. any individual CA.

## Shipped

- **v0.1.0** (2026-05-14) — initial public scaffold: license, policies,
  directory layout, JSON Schema 2020-12 placeholder for the AEP
  metadata, stub conformance vectors.
- **v0.1.1** (2026-05-15) — first runnable offline verifier
  (`@eatf/verifier`, TypeScript, ~1.4 kLOC) + `eatf-verify` Node CLI
  + four real `.aep` conformance vectors (3 valid + 1 invalid) + CI
  running `vitest` and `eatf-verify --conformance`.
- **v0.1.2** (2026-05-15) — `eatf-inspect` Node CLI (structural dump
  of an `.aep`) + full v0.1 wire-format specification in
  `docs/aep-profile.md` + real `metadata.json` schema (replacing the
  v0.1.0 aspirational manifest schema).

## Next — v0.1.3 (signer)

**Goal:** end-to-end round-trip. Today an external party can
verify `.aep` files; after v0.1.3 they can produce them.

- `@eatf/signer` Node/TS library — JCS canonicalisation → SHA-256
  → RSA-PSS sign → optional ML-DSA-65 sign → flat-layout ZIP
  packaging → optional RFC 3161 timestamp call (network optional;
  signer can write a placeholder TSA-less package for air-gapped
  use).
- `eatf-sign` Node CLI thin wrapper over `@eatf/signer`. Takes a
  payload, an issuer keypair, and an optional TSA URL; writes a
  `.aep` to disk. No network calls unless `--tsa <url>` is passed.
- Two new conformance vectors:
  - `valid/minimal-roundtrip/` — produced by `eatf-sign` from a
    known payload + dev keys checked into `test-vectors/keys/`,
    verifies clean with `eatf-verify`.
  - `valid/no-timestamp/` — same shape but without
    `timestamp.tsr`, demonstrating that the timestamp is optional
    for offline / air-gapped attestations.
- CI: a new `roundtrip` job that runs `eatf-sign` over a fixture
  payload and pipes the output to `eatf-verify`, asserting
  `verify=true`.

**Implementation note:** the signer is written **fresh** from the
spec in `docs/aep-profile.md`, not ported from the internal Java
backend. The internal backend's signing path is bound to tenant
management, audit ledger, and database services — those are out
of scope for the public release. Writing fresh is cleaner and
keeps the public signer narrow.

## v0.1.4 — failure-mode coverage + GitHub Action

**Goal:** expand the conformance set so external verifier
implementations can claim v0.1 conformance with confidence.

- Six new invalid vectors, one per failure mode:
  - `invalid/tampered-manifest/`
  - `invalid/bad-signature-classical/`
  - `invalid/bad-signature-mldsa/`
  - `invalid/untrusted-issuer/`
  - `invalid/expired-issuer/`
  - `invalid/bad-timestamp/`
  Each carries a `verify-expected.txt` with the diagnostic the
  verifier should report and a `README.md` describing the tamper.
- `tyche-institute/verify-aep-action@v1` — a small GitHub Action
  that downstream pipelines can drop into their workflow to assert
  every `.aep` produced by their build verifies cleanly. Composite
  action wrapping `eatf-verify`. ~50 LOC.
- Lives in a sibling public repo
  (`tyche-institute/verify-aep-action`) rather than this one so the
  marketplace listing is clean.

## v0.1.5 — OVERT receipt schema + doc fill-in

**Goal:** complete the documentation surface and add schema
validation for the second JSON document in the AEP (the OVERT
receipt).

- `schemas/overt-receipt-v1.schema.json` — JSON Schema 2020-12 for
  `overt_receipt.json`. CI validates every conformance vector's
  receipt against it.
- Fill in the remaining `docs/` pages from stubs to full
  specifications:
  - `docs/architecture.md` — full layered overview + per-module
    responsibilities mapped to `lib/src/*.ts`.
  - `docs/threat-model.md` — full STRIDE table, mapped to the
    eight verification checks in `lib/src/verifier.ts`.
  - `docs/attestation-profile.md` — W3C VC profile for the optional
    `attestations/agent.vc.json` entry (when EATF starts carrying
    one).
  - `docs/glossary.md` — expanded definitions.
  - `docs/design-rationale.md` — full reasoning for each design
    decision.

## v0.2.0 — Python verifier

**Goal:** open the ML / data-science / regulator audience.

- `lib-python/` — fresh port of the TypeScript verifier to Python
  3.11+. Stack:
  - [`pyca/cryptography`](https://cryptography.io/) for RSA, SHA,
    X.509.
  - [`oqs-python`](https://github.com/open-quantum-safe/liboqs-python)
    for ML-DSA-65.
  - [`asn1crypto`](https://github.com/wbond/asn1crypto) for CMS and
    RFC 3161 parsing.
  - `zipfile` from stdlib.
- `pip install eatf-verifier` — published to PyPI under the
  `tyche-institute` namespace.
- Same conformance contract as the TS verifier; tested against the
  same `test-vectors/`.
- CI: new `python-verifier` job that runs `pytest` and a
  conformance assertion.

**Explicit non-goal:** this is NOT a port of the existing internal
`sdks/python-sdk/aletheia/` package. That package is a managed-
service client for `api.aletheia.ai` (login/password, multi-tenant,
agent registration) and stays internal to the reference deployment.
The public Python package is purely a verifier with no network
surface.

## v0.3.0 — Go verifier

**Goal:** join the supply-chain / cloud-native ecosystem (sigstore,
in-toto, SLSA neighbourhood).

- `lib-go/` — fresh port. Stack:
  - `crypto/rsa`, `crypto/x509`, `crypto/sha256` from stdlib.
  - [`circl/sign/mldsa`](https://github.com/cloudflare/circl) for
    ML-DSA-65.
  - [`go.mozilla.org/pkcs7`](https://github.com/mozilla-services/pkcs7)
    (or in-tree CMS) for RFC 3161 token parsing.
  - `archive/zip` from stdlib.
- Published as a Go module:
  `github.com/tyche-institute/eatf/lib-go`.
- CI: new `go-verifier` job that runs `go test` and a conformance
  assertion.

## Parallel ongoing work (any version)

- **`pre-commit` hook** — verify every `.aep` in a working tree
  before commit. Tiny: just `eatf-verify` over a glob. Useful for
  teams that version evidence.
- **More test vectors** — every reported tamper class deserves its
  own vector. If you encounter a class of breakage not covered by
  `test-vectors/invalid/`, please open an issue or PR.
- **Documentation translations** — once the English `docs/` are
  filled in, translations welcome.

## Explicit non-goals

The following items have been considered and declined for the
public repository, even if requested. They would either reintroduce
managed-service surface, conflict with the project's eIDAS
positioning, or be outside the maintainer team's capacity to
support.

- **Backend reference implementation.** Tyche Institute's Java
  Spring backend is the operational backbone of the reference
  deployment at eatf.eu and stays proprietary. Anyone wanting to
  run their own EATF deployment is encouraged to write their own
  backend against the public spec and verifier; the spec is
  small enough to do this without copying any operator code.
- **Frontend reference implementation.** Same reasoning.
- **Managed-service client SDKs** (Python, JS, Java, etc.). These
  are tightly coupled to one operator's API surface and tenant
  conventions. We will open-source the **wire format** (any client
  can be built from the spec) but not the **client libraries**
  that talk to eatf.eu specifically.
- **Anything claiming eIDAS qualified status.** EATF is not an
  eIDAS trust service under Article 3(16); any feature implying
  otherwise (qualified signature issuance, QTSP integration as a
  feature of the framework rather than as an operator's choice,
  QEAA issuance) is out of scope. See `NOTICE` and
  [`docs/aep-profile.md`](./docs/aep-profile.md) for the
  positioning statement.
- **Rust verifier.** Maintainer-capacity decision. A community
  contributor is welcome to start one and we will reference it from
  the README if the implementation passes the conformance contract.
- **VS Code extension.** Same. Community contribution welcome.
- **Hosted "EATF marketplace" / agent registry.** EATF is a
  framework for verifiable self-attestation; it does not operate a
  registry of agents. Any registry-like layer is a deployment
  decision for individual operators, not a framework feature.

## How priorities are set

The version sequence above reflects two things:

1. **Dependency order.** A signer needs the wire format frozen
   (done in 0.1.2); a Python verifier needs the conformance set
   stable enough that we trust the contract (done in 0.1.1, will
   widen in 0.1.4); a Go verifier benefits from Python being there
   first as an additional reference.
2. **Adoption value per unit work.** The signer (0.1.3) and the
   GitHub Action (0.1.4) are the items most directly requested by
   downstream integrators today. Multi-language verifiers (0.2+)
   widen the audience but take more sustained work per port.

If you would benefit from a different order — for example, you need
the Python verifier sooner than the signer — please open an issue.
The roadmap is a default, not a contract.
