# lib/verifier

Offline verifier for Agent Evidence Packages.

## Inputs

1. The `.aep` package.
2. A configured set of issuer-CA trust anchors (PEM or DER).
3. A configured set of timestamping-authority trust anchors.

## What it checks

1. **Envelope integrity** — package is a well-formed ZIP, contains
   the required entries (`manifest.json`, `records/*.json`,
   `signatures/manifest.sig.cms`, `timestamps/manifest.tsr`,
   `certs/issuer.pem`, `certs/tsa.pem`).
2. **Manifest canonicalisation** — re-canonicalises `manifest.json`
   under JCS and asserts byte-for-byte equality with the signed copy.
3. **Hash chain** — every record file's `H(content)` matches the
   manifest's declared digest for that path.
4. **Classical signature** — verifies the manifest CMS signature
   against the issuer certificate.
5. **Post-quantum signature** — verifies the ML-DSA-65 signature if
   present.
6. **Issuer chain** — validates the issuer certificate up to a
   configured trust anchor (RFC 5280).
7. **Timestamp** — verifies the RFC 3161 TimeStampResp against the
   TSA trust anchor and asserts that it covers the manifest signature.
8. **Attestation** — if an `agent.vc.json` is present, validates the
   W3C VC against the embedded proof and the configured issuer.

## Outputs

A structured `VerificationReport`:

```json
{
  "verify": true,
  "issuer": "CN=Acme Operator Issuing CA 1",
  "signedAt": "2026-05-14T08:42:11Z",
  "checks": {
    "envelope": "pass",
    "manifest": "pass",
    "hashChain": "pass",
    "classicalSignature": "pass",
    "postQuantumSignature": "pass",
    "issuerChain": "pass",
    "timestamp": "pass",
    "attestation": "pass"
  }
}
```

Any failed check fails the overall verify and is reported with a
diagnostic code.

## v0.1.0 status

Stub. Reference implementation lands in a 0.1.x point release.
