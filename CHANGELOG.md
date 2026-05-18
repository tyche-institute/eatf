# Changelog

All notable user-facing and architecture-level changes to **Aletheia AI** are tracked here, grouped by sprint.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Semantic versioning is used for release tags.

Sprints are tracked as GitHub Milestones in the source repository; sub-issues live on the maintainer's delivery board.

---

## [Unreleased] — Tyche Institute rebrand

Site rebranding and risk-surface cleanup for `eatf.eu`. The site now
presents the EATF / Aletheia AI project as open-source research
infrastructure maintained by **Tyche Institute** (Estonian non-profit,
registration in progress), not as a commercial product.

### Why

Commercial framing on the public site created legal risk under a
non-compete clause in the maintainer's employment contract with an
eIDAS QTSP. A non-profit institutional wrapper (Estonian MTÜ, "Tyche
Institute") is being established to formally own the project; the
public site needs to match that positioning before any
commercial-flavoured copy reaches an employer, regulator, partner, or
journalist.

### Changed (brand and entity)

- **Operator entity:** introduced **Tyche Institute** (Estonian non-profit,
  registration in progress) as the operator of the EATF reference
  implementation.
- **Project name:** unchanged. Continues as **EATF** (Agent Trust
  Framework, also referred to as Aletheia AI). The "E" is retained for
  brand continuity but is no longer expanded as "Enterprise Agent Trust
  Framework" anywhere on the site — the expansion is now "Agent Trust
  Framework".
- **Domain:** unchanged (`eatf.eu`).
- **Logo wordmark:** removed "Enterprise" from the SVG and React
  components; the wordmark now reads "Agent / Trust Framework".
- **Site title and metadata:** rewritten to lead with the open-source
  research positioning and Tyche Institute attribution; added
  Open Graph and Twitter card tags.

### Changed (page-level cleanup)

- **/landing**: hero rewritten around the open-source / institutional
  framing; commercial CTAs removed.
- **/about**: rewritten to lead with Tyche Institute as the entity, EATF
  as its project; added "The name" section explaining the Tyche / Τύχη
  pronunciation and cryptographic-randomness motif.
- **/architecture**: title changed to "Aletheia AI / EATF — Architecture";
  Layer 1 status labels switched from PRODUCTION to the new
  IMPLEMENTED / ALIGNED / REFERENCED / ADDRESSED scheme; status legend
  expanded with descriptions; clarifying note added that PRODUCTION
  refers to reference deployments, not external certification.
- **/compliance**: retitled "EU AI Act regulatory mapping"; disclaimer
  added at the top; pricing and "Request a pilot" CTAs removed; schema.org
  publisher / author switched to `ResearchOrganization` (Tyche Institute).
- **/trust**: research disclaimer banner added.
- **/legal/[slug]**: every legal page now renders an institutional
  research-document disclaimer banner above the markdown content. Source
  files (`docs/legal/TSPS.md`, `docs/legal/etsi-en-319-401-self-assessment.md`,
  `docs/legal/termination-plan.md`, `docs/legal/threat-model.md`,
  `docs/legal/disclosure-policy.md`, `docs/specs/aep-profile-v1.md`) carry
  matching operator-update notes naming Tyche Institute. Substantive
  controls and findings are unchanged.
- **/developers**: reframed as "Researcher access & technical
  evaluation"; commercial language removed.
- **/auth/signin** and **/welcome**: rewritten copy emphasising research
  access; "Open workspace" CTA replaced with "Researcher access".
- **/use-cases** and **/demo/use-cases**: the "Enterprise HR" industry
  category renamed to "HR"; framed as reference scenarios, not customer
  deployments.
- **/roi**: reframed as a research planning estimator; the "Enterprise"
  company-size tier renamed to "Very large".
- **/privacy** and **/terms**: rewritten introductions to name Tyche
  Institute as the operator and to drop the "Enterprise" expansion.

### Removed

- **/pricing** route deleted entirely. `next.config.mjs` now permanently
  redirects `/pricing` → `/about` so any old links land on the
  institutional framing instead of a 404.
- "Pricing" link removed from header, footer, and compliance "next steps"
  cards. All EUR price quotes, sales-flavoured CTAs ("Talk to us",
  "Request Regulated", "Contact partnerships"), and tier names
  (Free / Starter / Growth / Scale / Regulated / Component) removed.
- Public link to private GitHub repository removed from the footer trust
  pills (replaced with a "Public release Q3 2026" placeholder); the
  architecture page's `docs/architecture-diagram-source.md` link replaced
  with a placeholder for the same reason.

### Added

- `docs/rebrand-notes.md` — summary of changes by page, list of TODO
  markers added for the post-MTÜ-registration follow-up, and suggested
  timeline for further updates.

### Notes

- Tyche Institute MTÜ registration with the Estonian e-Business Register
  is still in progress at the time of this commit. All copy referring to
  the operator uses "(Estonian non-profit, registration in progress)" or
  the equivalent. Source and content carry `TODO(tyche-mtu-registration)`
  markers at every location that needs to be revisited after registration
  completes — see `docs/rebrand-notes.md` for the inventory.
- Operational deployments on `matx.ee`, `h2oatlas.ee`, `eaudit.ee`, and
  `ai-act.eatf.eu` are out of scope for this PR; this cleanup is for the
  `eatf.eu` site itself.

---

## [v0.4.0-phase4-complete] — 2026-04-04

**Phase 4 (Policy & Coverage + Landing & Content) closed out.** Two full sprints delivered end-to-end; Phase 5 (Public API + SDKs) in progress.

### Sprint 3 — Phase 5 APIs/SDKs (2026-03-15 → 2026-04-04) · 60% done

Closed (3 of 5 sub-issues):

- **Public API (OpenAPI 3.0) and For Developers page** — `#13` · stable OpenAPI 3.0 spec for `POST /api/ai/ask`, `GET /api/ai/verify/:id`, `GET /api/ai/evidence/:id`, `GET /api/ai/verifier`; quickstart published on "For Developers" landing.
- **Sign-only API (`POST /api/sign`)** — `#14` · external systems can submit already-generated LLM responses for canonicalisation → hash → sign → (TSA) timestamp → persistence; integration-tested round-trip.
- **Python SDK (sign / verify / get_evidence)** — `#15` · `aletheia.sign()`, `aletheia.verify()`, `aletheia.get_evidence()` with mocked-HTTP unit tests; publishable to PyPI.

Rolled over to Sprint 4: `#16` (TypeScript SDK), parent `#51`.

### Sprint 2 — Phase 4 Landing & Content (2026-02-22 → 2026-03-14) · 85% done

Closed (6 of 7 sub-issues):

- **Landing Hero + CTA** — `#7` · new Hero «ИИ это сказал. Но по каким правилам?» + "Проверить ответ — Демо" CTA, Phase-4 alignment.
- **One scenario (HR or Legal)** — `#8` · 1–2 page scenario in `docs/en/scenarios/`, used as input for demo video.
- **Demo video (3–5 min)** — `#9` · screencast: question → answer → verify → evidence → offline verifier; published to landing.
- **Outreach to 10–20 companies** — `#11` · ≥10 emails sent, ≥3 discovery calls, ≥1 LOI collected.
- **Basic analytics** — `#12` · landing visit counters, CTA clicks, demo usage, evidence downloads.
- **Sprint 2 parent** — `#50` · closed with 85% DoD met.

Rolled over to backlog: `#10` (Use Cases page — scope re-scoped).

### Sprint 1 — Phase 4 Core: Policy & Coverage (2026-02-01 → 2026-02-21) · 100% done

Closed (6 of 6 sub-issues):

- **Demo-policy `aletheia-demo-2026-01`** — `#2` · canonical policy file + R1–R4 rule docs; default policy in dev profile.
- **Policy coverage in backend** — `#3` · coverage = evaluated / total_rules, persisted in DB, surfaced via `/api/ai/verify/:id`.
- **Policy coverage in Evidence Package** — `#4` · `.aep` now carries coverage + per-rule status (pass / not_evaluated).
- **UI: Display policy coverage** — `#5` · coverage block on `/verify`, expandable rule list with statuses.
- **UI: "Why confidence is not 100%?"** — `#6` · inline explanation of which checks passed / did not evaluate.
- **Sprint 1 parent** — `#49` · closed with 100% DoD met.

### Infrastructure & Process

- **Co-authorship trail** — 81 of 310 main-branch commits in this release carry `Co-authored-by: H3nr1R <…>` trailers; 2-person team attribution is now traceable in `git log` and on GitHub's contributors graph.
- **Branch protection** — `main` now requires PR + 1 approval + CODEOWNERS review + 4 required CI checks (Backend Tests (Java 21), Frontend Tests (Node.js 20), Python SDK Tests, All Checks Complete). Force-push and branch deletion disabled.
- **CODEOWNERS + TEAM.md** — PR `#54` · routes review automatically; documents the 2-person team composition.
- **Delivery board** — 23 issues + Status/Priority/Start-date/Target-date + labels on the maintainer's Projects v2 board.

---

## [Unreleased] — Sprint 4 (2026-04-05 → 2026-04-25) · in progress · 20% done

**Phase 5 integrations sprint.** Target: `v0.5.0-phase5-integrations` by 2026-04-25.

### In progress

- `#17` — **MCP Attestation documentation and optional API extension** (docs + API surface)
- `#20` — **Partner integration(s) — 1–2 partners** (contracts + reference implementation)
- `#52` — Sprint 4 parent (tracking)

### Closed so far

- `#18` — **SIEM event export** (response_generated, response_signed, evidence_created emitted as structured events; webhook delivery documented in `docs/en/integrations/SIEM.md`)

### To do

- `#19` — **Blockchain anchoring** (document or implement)

---

## Backup safety net

A snapshot of `main` immediately before the co-authorship rewrite is preserved on `origin/backup/pre-rewrite-2026-04-23` (SHA `caad2318`). The rewrite only added trailers; no content changes.

---

*Format: Sprint sections list closed sub-issues with a 1-sentence summary of user-visible or architectural impact. Infrastructure changes are collected separately per release.*
