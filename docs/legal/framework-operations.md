<!-- markdownlint-disable MD013 MD041 -->

# EATF Framework Operations Statement (v1.0)

> **This is a self-published research document representing the
> maintainer's analysis. It does not constitute a formal commitment,
> regulatory filing, or legal opinion.** Operator entity: Tyche
> Institute (Estonian non-profit, registration in progress). EATF is
> open-source research infrastructure under Apache 2.0 (public release
> planned Q3 2026 under `github.com/tyche-institute`).

**Document identifier:** `urn:eatf:framework-operations:1.0`
**Version:** 1.0, dated 2026-05-14.
**Status:** Public.
**Canonical URL:** `https://eatf.eu/legal/framework-operations`
**Issuer:** Tyche Institute (Estonian non-profit, registration in
progress), maintainer of the EATF research project (also referred to as
Aletheia AI).

---

## 1. Not a trust service

EATF is **not** an eIDAS trust service under Article 3(16) of
Regulation (EU) 910/2014. Tyche Institute:

- does **not** issue qualified certificates, qualified signatures,
  qualified timestamps, or qualified attestations;
- does **not** provide certificate issuance, timestamping, signing, or
  attestation as a service to external customers;
- does **not** operate as a Qualified Trust Service Provider (QTSP) or
  non-qualified TSP.

EATF agent attestations are technical self-attestations of agent
outputs — comparable to a software vendor signing its own binary, or
Git signing its own commits. They do **not** constitute Qualified
Electronic Attestations of Attributes (QEAA) under eIDAS Article 3(45)
and have no eIDAS legal effect.

This is a Framework Operations Statement: a non-TSP description of
how the EATF reference implementation is maintained and operated.
Tyche Institute does not operate as a Trust Service Provider, so this
document deliberately avoids ETSI TS 119 402 language for service-
provision claims.

## 2. What EATF is

EATF (Agent Trust Framework) is a specification and reference
implementation for cryptographically verifiable AI agent
self-attestation:

- **Specification:** the Agent Evidence Package (AEP) format,
  attestation profile, and conformance test vectors, open for
  community review.
- **Reference implementation:** cryptographic primitives, AEP package
  format library, offline verifier CLI, and example issuers/signers
  — published under Apache 2.0.
- **Reference deployments:** three deployments in research,
  educational, and pre-existing-engagement contexts that demonstrate
  framework capabilities — operated by community contributors in
  personal or academic capacity, not as commercial services. See
  [Reference deployments](/reference-deployments).

## 3. Operator entity

The maintainer of the EATF project is **Tyche Institute**, an Estonian
non-profit association (MTÜ) being established; registration with the
Estonian e-Business Register is in progress. Founder roles are
symbolic; technical work is performed by volunteer contributors and
advisors. The institute does not sell trust services, does not certify
compliance, and does not compete with commercial trust service
providers.

## 4. Private CA for agents

The reference implementation includes a Certificate Authority for
issuing certificates to agents operating within a deployment. This is
a **private CA for internal use**, structurally analogous to an
enterprise's internal CA. It is **not** a public trust service and
does **not** issue certificates to external relying parties as a
service.

Operators deploying EATF remain responsible for their own conformity
assessments under any applicable regulation, including (where
relevant) the EU AI Act, GDPR, NIS2, and sector-specific rules.

## 5. Standards relationships

EATF uses cryptographic primitives and data formats compatible with
eIDAS trust services where applicable, so that operators who choose to
plug in a third-party eIDAS Trust Service Provider (for example, a
qualified timestamping authority) can do so cleanly. See
[Standards reference](/standards) for the full list of relationships
(IMPLEMENTED / ALIGNED / REFERENCED / ADDRESSED). Notable points:

- **eIDAS 2.0** — *ALIGNED.* Cryptographic primitive and data-format
  compatibility, so operators can interoperate with eIDAS TSPs.
  EATF itself is explicitly not a TSP.
- **ETSI EN 319 401 (TSP General Policy Requirements)** —
  *REFERENCED.* Applies to Trust Service Providers; EATF is not a
  TSP. The earlier self-assessment artifact has been archived.
- **IETF RFC 3161 (Timestamp Protocol)** — *IMPLEMENTED* as a client.
  EATF can consume RFC 3161 timestamps from third-party TSAs; it does
  not provide timestamping as a service.
- **W3C Verifiable Credentials, FIPS 204 ML-DSA, RFC 5280 X.509, RFC
  8785 JCS** — *IMPLEMENTED* where used by the reference
  implementation.
- **EU AI Act** — *ADDRESSED.* The framework addresses Article-12,
  Article-13, and Article-14 record-keeping, transparency, and human
  oversight requirements at the protocol layer. This is not a
  conformity-assessment certification.

## 6. Project sustainability

The EATF reference implementation is released under Apache 2.0.
Maintainership transition, repository ownership, and continuity for
reference deployments are described in the
[Project Sustainability Plan](project-sustainability-plan.md).

## 7. Security and disclosure

Security issues are handled under the
[Coordinated Disclosure Policy](disclosure-policy.md). The
[STRIDE threat model](threat-model.md) is published as a research
document for peer review; it describes residual risks rather than
making compliance claims.

## 8. Related documents

- [Framework Operations Statement (this document)](framework-operations.md)
- [Project Sustainability Plan](project-sustainability-plan.md)
- [Coordinated Disclosure Policy](disclosure-policy.md)
- [STRIDE Threat Model](threat-model.md)
- [AEP Profile v1 specification](../specs/aep-profile-v1.md)
- [Reference deployments page](/reference-deployments)

## 9. Revision history

| Version | Date       | Notes                                                         |
|---------|------------|---------------------------------------------------------------|
| 1.0     | 2026-05-14 | Initial Framework Operations Statement.                       |
