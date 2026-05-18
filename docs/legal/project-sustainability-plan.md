<!-- markdownlint-disable MD013 MD041 -->

# EATF Project Sustainability Plan (v1.0)

> **This is a self-published research document representing the
> maintainer's analysis. It does not constitute a formal commitment,
> regulatory filing, or legal opinion.** Operator entity: Tyche
> Institute (Estonian non-profit, registration in progress). EATF is
> open-source research infrastructure under Apache 2.0.

**Document identifier:** `urn:eatf:sustainability:1.0`
**Version:** 1.0, dated 2026-05-14.
**Status:** Public.
**Canonical URL:** `https://eatf.eu/legal/project-sustainability-plan`
**Replaces:** earlier "Termination Plan" draft, preserved under
[`archive/2026-05-14/termination-plan-draft.md`](archive/2026-05-14/termination-plan-draft.md).

---

## 1. Scope and framing

This is an open-source-project sustainability plan, not a trust
service termination plan. EATF is not an eIDAS trust service under
Article 3(16), so the "fate of issued qualified certificates"
problem that ETSI EN 319 401 §7.12 addresses for Trust Service
Providers does not apply here. What this document covers instead:

- **Maintainership transition** — who can take over the project if
  the current maintainers step away.
- **Repository ownership** — where the source and specifications live
  and how to transfer them.
- **Reference deployment continuity** — what relying parties of the
  three reference deployments (h2oatlas.ee, matx.ee, eaudit.ee) can
  expect if a deployment is wound down.
- **Evidence package longevity** — how `.aep` evidence packages stay
  verifiable independent of any single hoster.

## 2. Maintainership transition

Tyche Institute is being established as an Estonian non-profit
association (MTÜ). Founder roles are symbolic; technical work is
performed by volunteer contributors and advisors.

If the current maintainers cannot continue:

1. The institute board, once registered, may appoint successors from
   active contributors.
2. The project is Apache 2.0; any party may fork it indefinitely and
   continue development. No "maintainer death" is fatal to users.
3. The GitHub organisation `tyche-institute` is the planned public
   home for the source (Apache 2.0 release planned Q3 2026). If the
   organisation lapses, the latest tagged release on the public
   mirror remains usable under Apache 2.0 terms.

## 3. Repository ownership

Source authoritative locations:

- **Specification and reference implementation:** planned
  `github.com/tyche-institute/eatf` under Apache 2.0.
- **Trust anchor mirror:** the `eatf-trust-anchors` repository
  mirrors public key history independently from the implementation
  repository; verifier deployments can pin to this mirror so trust
  anchors survive a maintainer transition.
- **archive.org and IPFS snapshots:** released artifacts and the
  trust-anchor mirror are mirrored independently for additional
  durability.

Transferring repository ownership: standard GitHub transfer is the
default mechanism. The Apache 2.0 license is irrevocable for already-
published versions; forks can continue under the same license.

## 4. Reference deployment continuity

The three reference deployments are operated by community
contributors in personal or academic capacity (see
[Reference deployments](/reference-deployments)). They are
demonstrations, not commercial services. If a reference deployment is
wound down:

- The operator should publish a notice on the deployment site with a
  reasonable lead time before shutdown.
- Existing `.aep` evidence packages remain verifiable offline (see
  §5).
- Relying parties who require commercial service guarantees should
  not depend on reference deployments — they should run their own
  EATF deployment from the Apache 2.0 reference implementation, or
  contract with an external commercial trust service.

## 5. Evidence package longevity

`.aep` Agent Evidence Packages are self-contained and verifiable
**offline** using the public Apache 2.0 verifier:

- The verifier reads only the `.aep` bytes plus a known public-key
  history (mirrored to `eatf-trust-anchors`, archive.org, and IPFS).
- No call to any Tyche-Institute-operated server is required for
  verification.
- The package format and verifier algorithms are open
  ([AEP Profile v1](../specs/aep-profile-v1.md)).

This means that once a `.aep` is produced, it stays verifiable for
the lifetime of the algorithms and the public-key history mirrors.
Continuity of any single deployment is not load-bearing.

## 6. What this plan deliberately does **not** cover

This document does **not** address:

- Fate of issued qualified certificates under eIDAS — EATF does not
  issue qualified certificates.
- Revocation of qualified trust service status — EATF does not hold
  qualified trust service status.
- TSP termination notifications to supervisory bodies under ETSI EN
  319 401 §7.12 — Tyche Institute is not a TSP.

The retired Termination Plan draft, which was written in TSP voice
and addressed these topics by analogy, is preserved for transparency
under [`archive/2026-05-14/termination-plan-draft.md`](archive/2026-05-14/termination-plan-draft.md).

## 7. Revision history

| Version | Date       | Notes                                                              |
|---------|------------|--------------------------------------------------------------------|
| 1.0     | 2026-05-14 | Initial Project Sustainability Plan (replaces Termination Plan).   |
