# test-vectors/ — conformance test vectors

Two sibling subdirectories:

- `valid/` — packages that MUST verify cleanly. Every implementation
  claiming v0.1 conformance must report `verify=true` for every
  package under this tree.
- `invalid/` — packages that MUST fail verification. Each subdirectory
  here exercises one specific failure mode (tampered record,
  bad timestamp, untrusted issuer, …). Each vector ships a
  `expected-failure.txt` naming the diagnostic code the verifier
  should report.

## Conformance reporting

A conformance run consists of:

1. Run the verifier against every `valid/<vector>/package.aep` and
   collect the `VerificationReport`.
2. Run the verifier against every `invalid/<vector>/package.aep` and
   collect the rejection code.
3. Emit a `conformance.json` mapping each vector to PASS/FAIL.
4. Submit (or publish) the report.

The reference verifier under `../lib/verifier/` is conformance-tested
against this set as part of CI.

## v0.1.0 status

Stub. Test vectors land alongside the runnable verifier in successive
0.1.x point releases. The directory layout (`valid/`, `invalid/`) is
the stable interface that external implementations can already plan
against.
