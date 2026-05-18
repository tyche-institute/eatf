# EATF Coordinated Disclosure Policy

> **Operator update (2026-05-14).** The operator entity for the EATF
> reference implementation is **Tyche Institute** (Estonian non-profit,
> registration in progress). This is a self-published research document
> representing the maintainer's analysis. It does not constitute a
> formal commitment, regulatory filing, or legal opinion. Substantive
> SLAs and safe-harbour terms unchanged in this revision.

**Version:** 1.0-draft, dated 2026-05-12 (operator-entity revision 2026-05-14). Comment period open through 2026-08-12.
**Owner:** Tyche Institute (Estonian non-profit, registration in progress), maintainer of the EATF research project.
**Scope:** the EATF research codebase, the public website at `eatf.eu`,
the reference backend at `api.eatf.eu` and `ws.eatf.eu`, the public
verifier and offline-verifier JAR, the published SDKs (`@eatf/cli`,
`eatf-python`), and reference partner integrations.

---

## 1. Why this document exists

EATF is open-source research infrastructure for cryptographically
verifiable AI agent attestation; it is **not** an eIDAS trust service
under Article 3(16) of Regulation (EU) 910/2014 and Tyche Institute
does not operate as a Trust Service Provider. The project's
credibility nevertheless rests on a publicly inspectable
incident-response and disclosure discipline. This policy is the
public contract between external security researchers, deployers of
the reference implementation, relying parties (auditors and verifying
counterparties), and the maintainer team.

It is intentionally short and concrete. The accompanying RFC 9116
`security.txt` at `https://eatf.eu/.well-known/security.txt` points here.

## 2. How to report

Pick the channel that matches the sensitivity of the finding:

| Channel | When to use |
|---|---|
| `security@eatf.eu` (PGP encouraged, key at `https://eatf.eu/.well-known/pgp.asc`) | Default — anything that should not be in a public issue. |
| GitHub private security advisory ([new advisory](https://github.com/tyche-institute/eatf/security/advisories/new)) | When you want to coordinate a fix directly with maintainers in the GitHub UI. |
| Signal / Wire / Matrix | On request via the email above. We will reply with a contact handle. |

Please **do not** report security issues through public GitHub issues,
public Discord/Telegram channels, or social media. If you accidentally
do, we will help you migrate the conversation off-channel.

## 3. What to include

To accelerate triage, include as much of the following as you can:

- **Type of vulnerability** (crypto, auth, injection, tenant isolation,
  supply chain, etc.).
- **Affected component** — file path, branch/commit SHA, deployed URL.
- **Reproduction steps** — copy-pasteable commands when possible.
- **Impact** — what an attacker can do, and what stops them today.
- **Proof-of-concept** (a redacted exploit is enough; we do not need
  customer data).
- **Suggested fix or pointer** to the line(s) you would touch.
- **Whether you have shared the finding with anyone else** (we will keep
  that confidential).

## 4. What you can expect from us — SLAs

These are contractual commitments, not aspirations. If we miss any of
them, we publish that miss in the next quarterly transparency note at
`https://eatf.eu/security#transparency`. The clock starts at the moment
your initial report hits the inbox.

| Step | SLA |
|---|---|
| **Acknowledgment of receipt** | 72 hours (best effort within 24 hours on business days). |
| **Initial severity assessment** + assignment of an internal owner | 7 days. |
| **Periodic status updates** while a fix is in development | every 14 days at minimum. |
| **Coordinated disclosure deadline** | 90 days from acknowledgment, extendable by mutual agreement when a fix is genuinely in flight. We will not extend silently. |
| **Public disclosure** | a GitHub security advisory + a written notice under `https://eatf.eu/security#notices` once the fix is deployed and verified. CVE assigned where the issue warrants one. |
| **Credit** | with your consent, on the advisory and in the `https://eatf.eu/security#hall-of-fame` page. |

We treat issues affecting **multi-tenant isolation**, **signing key
material**, **TSA integrity**, or **the public verifier** as Sev-1 by
default and shorten the internal-fix window to 14 days.

## 5. Scope and exclusions

**In scope:**

- All code in the EATF reference codebase on the `main` branch and any
  release tag (public mirror: `tyche-institute/eatf`).
- Deployed services at `eatf.eu`, `api.eatf.eu`, `ws.eatf.eu`.
- The offline verifier JAR (`backend/-Pverifier`) and the WASM verifier
  bundle (Phase 1.20) once shipped.
- Published SDKs `@eatf/cli` (npm), `eatf-python` (PyPI).
- The `partner-integrations/` directory in this repository.

**Out of scope:**

- Findings that require physical access to a maintainer's hardware.
- Social-engineering attacks against maintainers or contributors.
- Denial-of-service achievable only through volumetric flooding (we
  defer to Cloudflare's posture there; please report via Cloudflare).
- Findings against `*.eatf.eu` subdomains hosted by third parties
  (e.g. status pages, blog) when the third party owns the surface.
- Findings only reproducible against forks of the repository or against
  the offline `aletheiadb` H2 file used in dev.

If your finding is borderline, ask. We will tell you whether we will
treat it as in scope, with reasoning.

## 6. Safe harbour

We will not pursue legal action against, ask law enforcement to
investigate, or terminate accounts of researchers who:

1. Make a good-faith effort to follow this policy.
2. Avoid privacy violations, destruction of data, and interruption of
   service beyond what is strictly necessary to demonstrate the issue.
3. Give us reasonable time to fix the issue before public disclosure.
4. Do not exploit the issue beyond the proof-of-concept.

This safe harbour is offered in addition to whatever rights you already
have under EU law. It does not waive your rights or ours, but it is a
binding commitment by the maintainer team.

## 7. Bug bounty

There is **no monetary bounty programme today.** A formal programme via
HackerOne or Intigriti is planned in Phase 2 of the EATF roadmap once
SOC 2 Type II is complete; until then we offer:

- Public credit (with your consent) on the advisory and the Hall of Fame.
- Reference letters and LinkedIn endorsements for serious work.
- A "Trust Researcher" badge and listing on `eatf.eu` for researchers
  who have submitted Sev-1/Sev-2 findings.

We will update this section the moment a paid bounty programme opens.

## 8. PGP / encryption

The current PGP fingerprint is published at
`https://eatf.eu/.well-known/pgp.asc`. If the link 404s on first read,
ask via the email above — we may have rotated. Key rotations are
announced under `https://eatf.eu/security#notices` and reflected in the
`Expires` field of `security.txt`.

## 9. Version history

| Version | Date | Notes |
|---|---|---|
| 1.0-draft | 2026-05-12 | Initial draft. Coordinated with `frontend/public/.well-known/security.txt` and `SECURITY.md`. Phase 1 step 1.8 of the EATF roadmap. |

## 10. Related documents

- `SECURITY.md` — short version, top of repo.
- `frontend/public/.well-known/security.txt` — RFC 9116 machine-readable.
- `docs/legal/threat-model.md` — STRIDE threat model.
- `docs/legal/framework-operations.md` — non-TSP description of how
  the reference implementation is maintained and operated.
- `docs/legal/project-sustainability-plan.md` — open-source
  sustainability commitments.
- `docs/legal/public-mirror-policy.md` — how and what we mirror from
  the private aletheia-ai repository to the public `tyche-institute`
  GitHub organization, including the two-gate CI flow and scrubbing
  rules.
