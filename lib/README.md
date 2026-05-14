# lib/ — EATF reference implementation

This directory will hold the reference implementation of the EATF
cryptographic and packaging stack. Each subdirectory corresponds to
one of the layers documented in [`../docs/architecture.md`](../docs/architecture.md).

| Subdirectory       | Layer | Responsibility                                                                            |
|--------------------|-------|-------------------------------------------------------------------------------------------|
| `canonicalization/`| 2     | RFC 8785 JCS for JSON; deterministic ZIP layout for the AEP envelope.                     |
| `signer/`          | 3     | Hybrid signing: RSA-4096 (or ECDSA-P256) + ML-DSA-65 detached CMS signatures.             |
| `timestamping/`    | 4     | RFC 3161 client for binding manifest signatures to a trusted-third-party timestamp.       |
| `package/`         | 5     | AEP ZIP envelope construction, content-addressed hashing, attestation embedding.          |
| `verifier/`        | 6     | Offline verifier: signature, hash chain, timestamp, trust-anchor validation.              |

## v0.1.0 status

The v0.1.0 release ships the directory layout and per-subdirectory
README placeholders documenting the intended responsibility of each
module. The runnable implementation is being ported from the internal
research codebase and will land in successive 0.1.x point releases,
each with conformance test vectors under `../test-vectors/`.

Pinning to v0.1.0 today gives integrators a stable reference for the
project's positioning, license, and governance even before the
reference code lands.
