# test-vectors/invalid/

Packages that MUST fail verification under any v0.1-conformant
verifier. Each vector exercises one specific failure mode.

```
<vector-name>/
├── package.aep
├── expected-failure.txt     # the diagnostic code the verifier should report
├── anchors/
│   └── …
└── README.md                # what failure mode this vector exercises
```

Failure-mode categories planned for v0.1:

- `tampered-record` — content under `records/` does not match its
  manifest digest.
- `tampered-manifest` — manifest bytes do not match the signed copy.
- `bad-signature-classical` — classical signature does not verify.
- `bad-signature-mldsa` — ML-DSA-65 signature does not verify.
- `untrusted-issuer` — issuer certificate does not chain to the
  configured root anchor.
- `expired-issuer` — issuer certificate had expired at the signed time.
- `bad-timestamp` — RFC 3161 response does not cover the manifest
  signature, or fails TSA chain validation.
- `missing-attestation` — required attestation entry is absent or
  truncated.

## v0.1.0 status

Stub. Vectors land in successive 0.1.x point releases.
