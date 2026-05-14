# Threat model (stub)

**Status:** stub for v0.1.0. The full STRIDE table and assumption
list land in a 0.1.x point release.

## Scope

This document covers the threat model of the EATF reference
implementation (`lib/` and `cli/`) and the AEP wire format. It does
not cover the threat model of any specific deployment; operators are
expected to perform a separate deployment-level threat assessment
that incorporates this one as a component-level input.

## Assets to protect

1. **AEP authenticity** — a verifier must be able to detect any
   tampering with an action record, attestation, or signature.
2. **AEP timeliness** — a verifier must be able to assert that the
   package was sealed at or after a given trusted-third-party
   timestamp.
3. **Issuer-key custody** — the operator's signing key must remain
   confidential to the operator.
4. **Trust-anchor integrity** — the verifier's configured root
   anchors must be authentic.

## Adversary model

We assume an adversary who can:

- Read any AEP after issuance (packages may be shared widely).
- Modify any AEP after issuance and present a modified copy.
- Replay an old AEP at any time.
- Substitute their own signing key and a forged certificate chain,
  provided they cannot compromise the operator's private key or the
  verifier's configured root anchors.

We do **not** defend against:

- An adversary who has compromised the operator's signing key.
- An adversary who can substitute the verifier's configured trust
  anchors (this is a host-security problem outside our scope).
- Side-channel extraction of operator keys from a hardware token
  (this is the token vendor's threat model).
- Long-term cryptanalytic attacks against an entire signature suite
  (we ship hybrid classical + post-quantum signatures specifically
  to bound this risk).

## STRIDE summary

The full STRIDE table will enumerate Spoofing / Tampering /
Repudiation / Information disclosure / Denial of service / Elevation
of privilege per component, with mitigation status mapped to v0.1
implementation status.
