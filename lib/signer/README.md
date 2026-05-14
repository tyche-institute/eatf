# lib/signer

Hybrid classical + post-quantum signing of the AEP manifest.

## Suites

| Suite       | Purpose                                          | Suite identifier         |
|-------------|--------------------------------------------------|--------------------------|
| RSA-4096    | Classical signature for broad verifier coverage. | `urn:eatf:sig:rsa4096`   |
| ECDSA-P256  | Classical signature (alternate, smaller AEPs).   | `urn:eatf:sig:ecdsa-p256`|
| ML-DSA-65   | Post-quantum signature (FIPS 204).               | `urn:eatf:sig:mldsa-65`  |

A v0.1 AEP carries at least one classical signature and the ML-DSA-65
signature side by side as detached CMS structures under
`signatures/`. Verifiers MUST validate at least one classical
signature and MUST validate the ML-DSA-65 signature when present.

## Key formats

- PEM-encoded PKCS#8 private keys (filesystem mode).
- PKCS#11 token reference (HSM mode).
- Operator's choice; the signer module does not impose a custody
  policy.

## v0.1.0 status

Stub. Reference implementation lands in a 0.1.x point release.
