# Agent attestation profile (stub)

**Status:** stub for v0.1.0.

The attestation profile describes the format of the
`attestations/agent.vc.json` record carried inside an Agent Evidence
Package. The record is a W3C Verifiable Credential 2.0 document signed
by the deploying operator's private CA.

## Positioning

EATF agent attestations are technical self-attestations of agent
identity, capability claims, and operator-asserted bindings. They are
**not** Qualified Electronic Attestations of Attributes (QEAA) under
eIDAS Article 3(45) and have no eIDAS legal effect. They are not
issued by a Qualified Trust Service Provider; the signing CA is a
private CA operated by the deployment.

## Signing modes

Two modes are defined for v0.1:

1. **Private-CA mode (default).** The attestation is signed by an
   issuer key whose certificate chains to a private root operated by
   the deployment. Verifiers trust the chain only if they have been
   configured with the corresponding root anchor.
2. **External-issuer-bound mode.** The attestation carries an
   external proof referencing a credential issued by a third party
   (e.g. an external QTSP). EATF does not issue this external
   credential; it only carries the reference. Verifiers MUST validate
   the external credential against the external issuer's published
   trust list, not against EATF.

## Mandate vocabulary

The attestation MAY carry a `mandate` claim describing what the
operator has authorised the agent to do. The mandate vocabulary is a
non-normative starting point in v0.1 and is expected to evolve based
on community input.

The full attestation schema, signing rules, and verification rules
land in a 0.1.x point release.
