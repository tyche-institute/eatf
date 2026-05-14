# Design rationale (stub)

**Status:** stub for v0.1.0.

This document captures the *why* behind EATF's design choices.
Detailed discussions land in a 0.1.x point release; the headlines:

## Offline verification

Verifiers must work without network access and without API keys.
Operators frequently need to share an evidence package with auditors,
regulators, or research collaborators who cannot or will not
authenticate to a hosted verifier service. Requiring online
verification would (a) re-create the trust-service centralisation the
project is explicitly avoiding, and (b) introduce a single point of
operational failure for an artefact that should outlive its issuer.

The cost of offline verification is that revocation must be expressed
inside the package (or trusted at validation time from
independently-distributed CRLs / OCSP-stapled responses), and that the
verifier must hold the relevant trust anchors locally.

## Hybrid signing (RSA-4096 + ML-DSA-65)

We ship both a classical and a post-quantum signature side by side
on every package, rather than choosing one. Verifiers MUST validate
at least one; library-level helpers validate both by default. The
hybrid approach lets us deploy ML-DSA-65 today without waiting for
the entire verifier ecosystem to upgrade, and bounds the damage if
either suite is later found weak.

## Private CA for agents

Agent attestations are signed by a private CA operated by the
deploying organisation, not by a public QTSP. This is a deliberate
positioning choice: a public QTSP issuing per-agent certificates
would entangle EATF with eIDAS qualified-trust-service semantics
that do not yet apply cleanly to AI agents. By keeping the CA
private and the attestation explicitly non-QEAA, the project stays
out of the trust-service regulatory perimeter while still providing
cryptographically meaningful evidence.

## Open specification

The wire format, schemas, test vectors, and reference verifier are
published under Apache 2.0. There is no proprietary verifier and no
gated test-vector set. The intent is that any party can implement an
independent verifier from the published spec and conformance vectors
alone, with no commercial relationship to Tyche Institute required.

## Permissive license + DCO (not CLA)

Apache 2.0 grants the patent and copyright rights the project needs
to distribute. A Contributor License Agreement would add marginal
legal protection at substantial overhead; the Developer Certificate
of Origin gives equivalent attestation with a per-commit
`Signed-off-by:` trailer and is the convention used by the Linux
kernel, Kubernetes, Docker, GitLab and many other large open
projects.
