# Threat model

**Status:** v0.1 (2026-05-17).
**Scope:** the EATF reference implementation in this repository
(`lib/` + `cli/`) and the AEP wire format. Out of scope: any
specific operator deployment, the operator's key-custody policy,
the operator's choice of TSA, and any application built on top of
the verifier.

This document is a focused STRIDE analysis mapped to the eight-step
verification pipeline in [`lib/src/verifier.ts`](../lib/src/verifier.ts).
For the broader architecture see [`architecture.md`](architecture.md);
for the wire format see [`aep-profile.md`](aep-profile.md).

EATF is not a trust service under eIDAS Article 3(16); this threat
model accordingly does not claim to address Qualified Trust Service
threat categories (qualified certificate compromise, supervisory body
breach, etc.). Operators choosing to chain a qualified trust service
into their deployment own those threats at their own boundary.

## Assets

1. **Package authenticity** — a verifier must be able to detect any
   post-sign modification of the package.
2. **Package timeliness** — a verifier must be able to assert that
   the package was sealed at or after a trusted-third-party timestamp.
3. **Operator signing-key custody** — the operator's private key must
   remain confidential to the operator.
4. **Verifier trust-anchor integrity** — the verifier's configured
   issuer and TSA anchors must be authentic.
5. **OVERT receipt fidelity** — the receipt's `content_hash` and
   policy fields must remain consistent with `canonical.bin` and
   `metadata.json`.

## Adversary model

We assume an adversary who can:

- **A1.** Read any AEP after issuance. Packages may be shared widely.
- **A2.** Modify any AEP after issuance and present a modified copy
  to a verifier.
- **A3.** Substitute their own RSA key pair and forge a self-signed
  `public_key.pem`.
- **A4.** Mangle the embedded RFC 3161 timestamp token.
- **A5.** Modify `metadata.json` independently of `canonical.bin`
  (e.g. to change the policy decision presented to a downstream
  consumer).
- **A6.** Delete or rename ZIP entries.
- **A7.** Replay a stale AEP at any later time.

We do **NOT** defend against:

- **N1.** Operator-side compromise of the private signing key.
- **N2.** Substitution of the verifier's configured root anchors at
  the host-security level (file-system tampering on the verifying
  host).
- **N3.** Side-channel extraction of the operator's private key from
  an HSM (HSM vendor's threat model).
- **N4.** Long-term cryptanalytic breakdown of a single signature
  suite (which is why hybrid classical + post-quantum is shipped).
- **N5.** Downstream display attacks: a verifier that prints the
  package's metadata to a human MAY display malicious metadata even
  while the boolean `valid` is true. The verifier surfaces decoded
  metadata for the caller to interpret; UI presentation is the
  caller's responsibility.

## STRIDE table

The verifier executes nine checks in
[`lib/src/verifier.ts`](../lib/src/verifier.ts). Each row below maps
one or more STRIDE categories to the check that mitigates them.

| ID    | STRIDE       | Threat                                                                                       | Mitigation                                                                                                | Verifier step               | Conformance vector              |
|-------|--------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|-----------------------------|---------------------------------|
| T1    | T            | Adversary modifies `canonical.bin` to alter the attested payload.                            | SHA-256 of `canonical.bin` is compared to `hash.sha256`.                                                  | 4-5                         | `tampered-canonical-bin`        |
| T2    | T            | Adversary modifies `metadata.json` (e.g. flips policy_decision allow ↔ deny).                | OVERT receipt cross-checks `metadata.policy_decision` against `receipt.policy.decision` and several other fields. | 7                          | `tampered-metadata`             |
| T3    | T, R         | Adversary modifies `signature.sig` to forge or randomise the bytes.                          | RSASSA-PKCS1-v1_5 (Web Crypto verify) over `canonical.bin` rejects any post-sign modification.            | 6                           | `bad-signature-classical`       |
| S1    | S            | Adversary substitutes their own RSA key pair and re-signs the package.                       | Verifier's caller pins issuer trust anchors externally; the embedded `public_key.pem` is only trusted if the caller's policy says so. (When no pinning is configured, the verifier validates the signature against the embedded key — this proves whoever issued the embedded key signed the package, but does NOT prove they are the legitimate operator. Trust-anchor enforcement is the caller's responsibility.) | 6 (signature) + caller-side trust-anchor check | `untrusted-issuer`        |
| T4    | T, R         | Adversary replays or fabricates the RFC 3161 timestamp.                                      | pkijs parses the `TimeStampToken`, verifies `messageImprint` against `hash.sha256`, verifies SignerInfo signature against embedded TSA certificate, and optionally chains TSA cert to the verifier's pinned TSA root list. | 9                          | `bad-timestamp`                 |
| I1    | I            | Adversary deletes a required envelope entry to bypass a check.                               | Verifier enumerates required entries first and refuses the package on the first missing entry, before any cryptographic step runs. | 2                          | `missing-canonical-bin`         |
| R1    | R            | Issuer claims not to have signed a package they did sign.                                    | The verifier proves the signature relationship; non-repudiation comes from the operator's contractual posture around key custody (out of framework scope, but the cryptographic primitive supports it). | 6                          | (out of scope; framework-level) |
| E1    | E            | Adversary substitutes a Verifiable Credential with elevated capabilities into `attestations/agent.vc.json`. | The VC proof is verified against its configured issuer; the VC itself is a self-attestation, not a capability grant. EATF does not enforce VC-based capability decisions — those are policy-engine concerns. | (W3C VC parsing layer; not in v0.1 verifier) | (none yet — v0.2 work)        |
| D1    | D            | Adversary submits a very large package to exhaust verifier memory.                           | `lib/` uses streaming-safe primitives where possible; callers SHOULD cap input size before calling `verify()`. Web Crypto + pkijs each allocate proportional to input size. | caller-side input cap       | (none — operator deployment-level) |
| R2    | R            | OVERT receipt's `content_hash` no longer references the embedded payload (e.g. the receipt was substituted from a different package). | Verifier confirms `receipt.content_hash == "sha256:" + SHA-256(canonical.bin)` and that every `witness.signature_refs[]` and `witness.timestamp_refs[]` entry exists in the package envelope. | 7                          | `tampered-overt-receipt`       |
| A7-R | (Replay)     | Adversary replays a stale-but-valid AEP at a much later date when underlying conditions have changed. | The verifier reports the RFC 3161 `genTime` so the caller can decide whether the timestamp is recent enough for their use case. The framework does NOT enforce a maximum age; that is a caller-policy decision. | 9 (genTime exposure)      | (caller policy)                |

## Residual risks (acknowledged)

- **No HSM verification at framework level.** The verifier cannot
  tell whether the signing key was kept in an HSM or on disk on the
  operator's laptop. Operators wanting hardware-key assurance must
  publish that posture in their Framework Operations Statement and
  the verifying party trusts (or doesn't) that assertion.
- **No transparency log.** Each AEP is verified standalone. We have
  no append-only public log of "every package ever issued by this
  operator". A community-run transparency log (sigstore Rekor-style)
  is an open direction — see the article-in-progress at
  `~/projects/tyche-research-vault/outlines/on-the-crossroads-marketplace-vs-distributed-trust.md`
  for the design discussion.
- **No revocation.** A compromised operator key cannot be revoked
  through the framework. Operators publish key-rotation events in
  their public-key history mirror
  ([`tyche-institute/eatf-trust-anchors`](https://github.com/tyche-institute/eatf-trust-anchors)
  for the reference deployment); verifiers MAY refuse packages whose
  signing key has been retired.
- **Cross-language verifier conformance.** v0.1 has only the
  TypeScript verifier. Conformance against `test-vectors/` defines
  correctness; independent ports in Python (planned v0.2.0) and Go
  (planned v0.3.0) are how we'll empirically validate the contract.

## Future hardening directions (not in v0.1)

- **Transparency log integration.** Opt-in adapter for an append-
  only public log of package digests (sigstore Rekor-style). Stays
  optional so the offline-verification property remains intact.
- **Revocation surfacing.** Verifier could consult a published
  revocation list at request time, with the call kept opt-in to
  preserve offline operation.
- **Capability VC profile.** A formal W3C VC profile for the
  `attestations/agent.vc.json` entry that downstream policy engines
  can interpret consistently.
- **HSM-attested signing posture field.** A metadata field where
  the operator can attest "signed under HSM-managed key" with a
  cryptographic proof rather than a textual claim.

## Vector-to-threat mapping

The conformance vectors in [`test-vectors/`](../test-vectors/) each
exercise one row of the STRIDE table above. Independent verifier
implementations claiming v0.1 conformance MUST reject every invalid
vector (with any diagnostic text) — that proves the corresponding
threat is mitigated.

## Related documents

- [`aep-profile.md`](aep-profile.md) — the wire format being threat-
  modelled.
- [`architecture.md`](architecture.md) — layered structure and where
  each check runs.
- [`design-rationale.md`](design-rationale.md) — why these specific
  primitives, why hybrid signing, why no registry.
