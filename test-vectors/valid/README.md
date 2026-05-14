# test-vectors/valid/

Packages that MUST verify cleanly under any v0.1-conformant verifier.

Each vector is a self-contained subdirectory:

```
<vector-name>/
├── package.aep
├── expected-verify.json     # the VerificationReport a verifier should produce
├── anchors/
│   ├── issuer-root.pem
│   └── tsa-root.pem
└── README.md                # what this vector exercises
```

## v0.1.0 status

Stub. Vectors land in successive 0.1.x point releases.
