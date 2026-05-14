# Agent Evidence Package (AEP) — wire-format profile (stub)

**Status:** stub for v0.1.0. Full specification lands in a 0.1.x
point release.

**Profile URN:** `urn:eatf:spec:aep:1.0`

## Goal

The Agent Evidence Package is a self-contained, offline-verifiable
artefact that documents an agent's actions and outputs. A verifier
with no network access and no API keys must be able to assess the
package's authenticity, integrity, and timeliness from the artefact
alone, given (a) the package, (b) the issuer's certificate or trust
anchor, and (c) a trust-anchor for the timestamping authority.

## High-level structure

An AEP is a ZIP archive with a stable internal layout:

```
package.aep/
├── manifest.json          # JCS-canonicalised manifest (RFC 8785)
├── records/
│   ├── 0001-action.json   # one action record per file
│   └── 0002-output.json
├── attestations/
│   └── agent.vc.json      # W3C VC; private-CA-signed agent self-attestation
├── signatures/
│   ├── manifest.sig.cms   # CMS detached signature over manifest.json
│   └── manifest.sig.mldsa # ML-DSA-65 detached signature over manifest.json
├── timestamps/
│   └── manifest.tsr       # RFC 3161 TimeStampResp covering H(manifest.sig.cms)
└── certs/
    ├── issuer.pem
    └── tsa.pem
```

The full byte-level layout, hash-chain construction, canonicalisation
rules, signature suites, and timestamp-binding rules are specified in
the upcoming full document.

## Non-goals

- AEP is **not** a Qualified Electronic Attestation of Attributes
  (QEAA) under eIDAS Article 3(45). It is a technical
  self-attestation by the agent and its operator.
- AEP is **not** a substitute for an audit log written to durable
  storage by the operator. It is a portable receipt that complements
  such logs, not a replacement.
- AEP does not standardise the semantics of what an agent's action
  records describe; it only standardises the envelope.

See [`design-rationale.md`](./design-rationale.md) for the reasoning
behind each design choice.
