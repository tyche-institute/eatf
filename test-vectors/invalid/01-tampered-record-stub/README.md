# test-vectors/invalid/01-tampered-record-stub

**Expected:** `verify=false`, diagnostic `tampered-record`.

This vector exercises the tampered-record failure mode: the content
under `records/0001-action.json` does not match the digest declared in
the manifest. A v0.1-conformant verifier MUST reject the package and
report the `tampered-record` diagnostic.

**Stub note (v0.1.0).** Like its valid sibling, this vector currently
ships the manifest only; the full `.aep` ZIP envelope with the
intentionally-mismatched record lands alongside the runnable verifier
in 0.1.x. The manifest above is itself schema-valid — the tamper is
in the record-vs-digest mismatch which the schema cannot catch.

`verify-expected.txt` is the stub conformance contract consumed by
`cli/eatf-verify/eatf-verify` until the runnable verifier lands.
