# EATF — Agent Trust Framework

EATF is an open-source reference implementation and specification for
cryptographically verifiable AI agent self-attestation, maintained by
Tyche Institute (Estonian non-profit research entity, registration in
progress).

## What EATF is

- A specification for **Agent Evidence Packages (AEP)** — signed,
  timestamped, offline-verifiable bundles documenting agent actions
  and outputs.
- A reference implementation in JavaScript/TypeScript and Java for
  producing, signing, and verifying AEPs.
- A set of test vectors and tools for conformance verification.
- Reference deployments in academic, educational, and family-business
  contexts demonstrating framework capabilities.

## What EATF is NOT

EATF is **NOT** an eIDAS trust service under Article 3(16) of
Regulation (EU) 910/2014. EATF does not:

- Issue qualified certificates, signatures, timestamps, or
  attestations.
- Provide certificate issuance, timestamping, signing, or attestation
  as a service to external customers.
- Operate as a Qualified Trust Service Provider (QTSP) or
  non-qualified TSP.

EATF agent attestations are technical self-attestations of agent
outputs. They **do not constitute** Qualified Electronic Attestations
of Attributes (QEAA) under eIDAS Article 3(45) and have no eIDAS
legal effect.

The reference implementation includes a private Certificate Authority
for issuing certificates to agents within a deployment. This is a
**private CA for internal use**, not a trust service. Operators
deploying EATF remain responsible for their own conformity
assessments under any applicable regulation.

## License

Apache License 2.0. See [LICENSE](./LICENSE).

## Quick start

Verify a sample evidence package using the bundled conformance vectors:

```bash
git clone https://github.com/tyche-institute/eatf
cd eatf

# Build the verifier
(cd lib && npm install && npm run build)
# Wire up the CLI
(cd cli/eatf-verify && npm install)

# Run conformance against the bundled vectors
node cli/eatf-verify/bin/eatf-verify.js --conformance test-vectors/
# → PASS  package.aep  expected=true   actual=true
# → PASS  package.aep  expected=true   actual=true
# → PASS  package.aep  expected=true   actual=true
# → PASS  package.aep  expected=false  actual=false
# → Conformance: 3 verified, 1 rejected, 0 contract mismatches.

# Verify your own .aep
node cli/eatf-verify/bin/eatf-verify.js path/to/your.aep
```

The signer that produces `.aep` files lands in a 0.1.x point release.
See [`docs/aep-profile.md`](./docs/aep-profile.md) for the wire
format specification.

## Documentation

- [Architecture](./docs/architecture.md) — layered overview of the
  reference implementation and the standards-relationship legend.
- [AEP profile specification](./docs/aep-profile.md) — the canonical
  Agent Evidence Package format (ZIP layout, JCS canonicalisation,
  hybrid RSA-4096 + ML-DSA-65 signing).
- [Attestation profile specification](./docs/attestation-profile.md)
  — agent attestation record format and signing modes.
- [Threat model](./docs/threat-model.md) — STRIDE-style trust
  boundaries, residual risks, planned mitigations.
- [Design rationale](./docs/design-rationale.md) — why offline
  verification, why hybrid signing, why private CA, why open
  specification.
- [Glossary](./docs/glossary.md) — IMPLEMENTED / ALIGNED / REFERENCED
  / ADDRESSED labels, AEP / VC / TSA terminology.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). This project uses the
**Developer Certificate of Origin** (DCO) — every commit must carry
a `Signed-off-by:` trailer. No Contributor License Agreement.

## Security

See [SECURITY.md](./SECURITY.md) for the vulnerability disclosure
policy.

## Reference deployments

EATF reference deployments demonstrate framework capabilities in
research and educational contexts. They are operated by community
contributors in personal or academic capacity and are not commercial
service offerings:

- **h2oatlas.ee** — Academic research deployment in an environmental
  data context.
- **matx.ee** — Educational technology project from a hackathon (math
  teaching tools).
- **eaudit.ee** — Technical advisory deployment within a pre-existing
  construction sector engagement.

The EATF reference implementation is available here under Apache 2.0
for any party wishing to deploy independently. Reference deployment
operators are responsible for their own configuration, security, and
applicable regulatory compliance. Tyche Institute publishes the
framework specification and reference implementation; it does not
operate or warrant individual deployments.

## About Tyche Institute

Tyche Institute is being established as an Estonian non-profit
association (MTÜ) advancing open standards and reference
implementations for verifiable AI agent attestation infrastructure.

## Status

**v0.1.1** ships the first runnable offline verifier:

- [`lib/`](./lib/) — `@eatf/verifier` 0.1.1 TypeScript implementation
  of the eight-check verification pipeline (envelope, canonicalisation,
  hash chain, RSA / ECDSA, ML-DSA-65, issuer chain, RFC 3161 timestamp,
  attestation). Runs in Node 20+ and in the browser.
- [`cli/eatf-verify/`](./cli/eatf-verify/) — `@eatf/verify-cli` 0.1.1,
  offline command-line wrapper.
- [`test-vectors/`](./test-vectors/) — four conformance vectors with
  real `.aep` files (3 valid + 1 invalid).

The signer, AEP packaging tooling, and additional CLI commands
(`eatf-sign`, `eatf-inspect`) land in successive 0.1.x point
releases. See the [CHANGELOG](./CHANGELOG.md) for per-release
contents and [`test-vectors/README.md`](./test-vectors/README.md) for
the conformance contract any independent implementation can verify
against.
