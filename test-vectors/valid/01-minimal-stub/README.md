# test-vectors/valid/01-minimal-stub

**Expected:** `verify=true`.

This vector exercises the minimum well-formed AEP manifest shape:
profile URN, issuer with `commonName` + SHA-256 fingerprint, one
action record with content-addressed digest, both classical and
post-quantum manifest signatures present, and an RFC 3161 timestamp
reference.

**Stub note (v0.1.0).** This vector ships the manifest only; the full
`.aep` ZIP envelope (with actual record bytes, CMS signatures, ML-DSA
signature, and a TSR) lands alongside the runnable verifier in
0.1.x. The schema-validation half of the conformance loop is already
testable today: `manifest.json` here MUST validate against
`schemas/aep-v1.schema.json`.

`verify-expected.txt` is the stub conformance contract consumed by
`cli/eatf-verify/eatf-verify` until the runnable verifier lands.
