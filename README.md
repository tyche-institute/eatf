# EATF — Agent Trust Framework

EATF is an open-source reference implementation and specification for
cryptographically verifiable AI agent self-attestation, maintained by
Tyche Institute (Estonian non-profit research entity, registration in
progress).

## What EATF is

- A specification for **Agent Evidence Packages (AEP)** — signed,
  timestamped, offline-verifiable bundles documenting agent actions
  and outputs.
- Two independent reference implementations — TypeScript
  ([`lib/`](./lib/)) and Python ([`lib-python/`](./lib-python/)) —
  for producing, signing, and verifying AEPs. A Go implementation is
  planned for v0.3.0 (see [ROADMAP.md](./ROADMAP.md)).
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

End-to-end round-trip using the bundled conformance vectors and dev
key:

```bash
git clone https://github.com/tyche-institute/eatf
cd eatf

# Build the verifier (which now also exports the signer).
(cd lib && npm install && npm run build)
# Wire up the CLIs.
(cd cli/eatf-verify && npm install)
(cd cli/eatf-sign && npm install)

# Run conformance against the bundled vectors.
node cli/eatf-verify/bin/eatf-verify.js --conformance test-vectors/
# → PASS … expected=true   actual=true   (×4)
# → PASS … expected=false  actual=false  (×1)
# → Conformance: 4 verified, 1 rejected, 0 contract mismatches.

# Sign your own payload with the dev key.
echo "Hello, world." > /tmp/payload.txt
cat > /tmp/meta.json <<'JSON'
{
  "schema": "urn:eatf:spec:aep:metadata:1.0",
  "attestation_id": "att_demo_01",
  "created_at": "2026-05-15T00:00:00Z",
  "agent_id": "urn:eatf:tenant:demo:agent:hello",
  "action_type": "demo.hello-world",
  "policy_id": "atap-basic",
  "policy_version": "1.0",
  "policy_coverage": 1.0,
  "policy_decision": "allow",
  "format_version": "ATAP-1.0"
}
JSON
node cli/eatf-sign/bin/eatf-sign.js \
  --payload /tmp/payload.txt \
  --key test-vectors/keys/dev-rsa-4096.key \
  --public-key test-vectors/keys/dev-rsa-4096.pem \
  --metadata /tmp/meta.json \
  --scope foundational:aep-response \
  --timestamp test-vectors/valid/valid-overt-profile/package.aep:timestamp.tsr \
  --out /tmp/hello.aep

# Verify what we just signed.
node cli/eatf-verify/bin/eatf-verify.js /tmp/hello.aep
# → verify=true
```

See [`docs/aep-profile.md`](./docs/aep-profile.md) for the wire
format specification and [`cli/eatf-sign/README.md`](./cli/eatf-sign/README.md)
for how to mint a fresh RFC 3161 timestamp from a public TSA.

## Documentation

- [Architecture](./docs/architecture.md) — layered overview of the
  reference implementation and the standards-relationship legend.
- [AEP profile specification](./docs/aep-profile.md) — **the
  normative wire format** for Agent Evidence Packages (ZIP layout,
  JCS canonicalisation, hybrid classical + ML-DSA-65 signing). The
  conformance contract for alternative implementations is defined
  here.
- [Attestation profile specification](./docs/attestation-profile.md)
  — agent attestation record format and signing modes.
- [Threat model](./docs/threat-model.md) — STRIDE-style trust
  boundaries, residual risks, planned mitigations.
- [Design rationale](./docs/design-rationale.md) — why offline
  verification, why hybrid signing, why private CA, why open
  specification.
- [Glossary](./docs/glossary.md) — IMPLEMENTED / ALIGNED / REFERENCED
  / ADDRESSED labels, AEP / VC / TSA terminology.

## Roadmap

See [ROADMAP.md](./ROADMAP.md) for what's planned (signer + sign
CLI, more failure-mode test vectors, GitHub Action, Python and Go
verifiers) and what's explicitly out of scope (backend, frontend,
managed-service client SDKs).

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

**v0.2.1** continues the two-implementation line — second,
independent verifier in Python, same wire format, same
conformance contract, zero shared code with the TypeScript
reference. v0.2.1 adds the TSA chain-to-root pin check that v0.2.0
promised for the Python side, mirroring `verifyTsaTrust` in TS
against the same three pinned DigiCert public roots:

- [`lib/`](./lib/) — `@eatf/verifier` (TypeScript / Node 20+ /
  browser). Exports both `verify()` and `sign()`. Full pipeline:
  envelope, canonicalisation, hash chain, RSA, ML-DSA-65, issuer
  chain, RFC 3161 timestamp, OVERT receipt.
- [`lib-python/`](./lib-python/) — `eatf-verifier` (Python 3.11+).
  Fresh port; same `verify=true | false` contract; `eatf-verify-py`
  CLI with `--conformance`, `--batch`, `--json` modes. PyPI publish
  planned; install today via `pip install -e ./lib-python`.
- [`cli/eatf-verify/`](./cli/eatf-verify/) — `@eatf/verify-cli`
  offline verifier CLI (Node).
- [`cli/eatf-sign/`](./cli/eatf-sign/) — `@eatf/sign-cli` offline
  signer CLI (no network; RFC 3161 token supplied as a file).
- [`cli/eatf-inspect/`](./cli/eatf-inspect/) — `@eatf/inspect-cli`,
  structural dump.
- [`test-vectors/`](./test-vectors/) — eleven shared conformance
  vectors (4 valid + 7 invalid). Both the TypeScript and Python
  verifiers must agree on every vector; CI enforces it.
- [`schemas/`](./schemas/) — JSON Schema 2020-12 for
  `metadata.json` and `overt_receipt.json`.
- [`test-vectors/keys/`](./test-vectors/keys/) — public dev RSA
  keypair (private key intentionally in repo so anyone can
  regenerate the round-trip vector and confirm byte-equality).

Coming next (per [ROADMAP.md](./ROADMAP.md)): Go verifier (v0.3.0).
