<!-- markdownlint-disable MD013 MD028 MD034 MD036 MD060 -->

# Agent Trust Framework

> **External name:** **EATF** — Agent Trust Framework.  
> **Internal codename:** **Aletheia AI** (repository and implementation name).

> **Current status:** early-stage trust platform with production-style architecture and explicitly experimental surfaces. **Not legal advice.**

[![Java](https://img.shields.io/badge/Java-21-orange?logo=openjdk)](https://openjdk.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5-brightgreen?logo=spring)](https://spring.io/projects/spring-boot)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Context](https://img.shields.io/badge/Context-QTSP%20experience-lightgrey)
[![PQC](https://img.shields.io/badge/PQC-ML--DSA--65-teal)](docs/developers/en/PLAN_PQC.md)

[![CI](https://img.shields.io/github/actions/workflow/status/tyche-institute/eatf/ci.yml?branch=main&logo=githubactions&label=CI)](https://github.com/tyche-institute/eatf/actions/workflows/ci.yml)
[![Open issues](https://img.shields.io/github/issues/tyche-institute/eatf?logo=github)](https://github.com/tyche-institute/eatf/issues)
[![Open PRs](https://img.shields.io/github/issues-pr/tyche-institute/eatf?logo=github)](https://github.com/tyche-institute/eatf/pulls)
[![Last commit](https://img.shields.io/github/last-commit/tyche-institute/eatf/main?logo=git)](https://github.com/tyche-institute/eatf/commits/main)

**EATF** is an early-stage, pilot-oriented trust and governance layer for agent actions in regulated or high-consequence workflows. It is built for **operators**, **integrators**, **auditors**, and **platform teams** who need a concrete answer to five questions:

1. how to control sensitive agent actions;
2. how to require human approval when risk is high;
3. how to issue signed evidence for what happened;
4. how to verify that evidence independently;
5. how to integrate those controls into existing systems.

The core product chain is simple:

1. control sensitive agent actions;
2. require human approval where risk is high;
3. generate signed evidence for what happened;
4. verify that evidence independently;
5. integrate those controls into existing systems.

The architecture question underneath that product promise is PKI-native: where do **agent output and governed action** sit in a **trust stack** you already know (**X.509 path logic, signature verification, revocation, timestamps, audit discipline** under **eIDAS** and **ETSI EN 319 xxx**)? From there we map how that reference architecture relates to **EU AI Act** traceability and integrity language without treating the Act as a PKI spec.

_PKI / QTSP experience informs the design; this repository is **not** a QTSP product._

The repository combines:

- a working product surface for governed actions, evidence, verification, audit, and partner integration;
- a set of demo and showcase flows used for presentations and exploration;
- research and vision material that explains why the architecture exists.

That distinction matters. Some surfaces are suitable for pilot-style evaluation; others remain explicitly experimental or explanatory. The primary product jobs are:

- **Operator** — govern actions, inspect trust state, review audit outcomes;
- **Integrator** — connect agents, manifests, APIs, and partner systems;
- **Auditor** — verify evidence, inspect disclosures, and export reports;
- **Admin** — manage tenant controls, identities, and safety levers.

The core implementation argument in code is still the same: **hash → sign → optional RFC 3161 timestamp → evidence package**, plus **path validation**, **OCSP/CRL**, and **hybrid classical + post-quantum** signing where enabled.

**Primary law (AI Act):** [Regulation (EU) 2024/1689 — EUR-Lex (consolidated EN)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) · **Navigator (unofficial, convenient):** [artificialintelligenceact.eu](https://artificialintelligenceact.eu/) — use EUR-Lex for authoritative text.

> **Want to plug an agent in?** [`partner-integrations/QUICKSTART.md`](partner-integrations/QUICKSTART.md) is the five-minute, copy-paste path: mint a key → `eatf init` → `eatf doctor` → `eatf agents sync` → `eatf sign --download` → `eatf verify`. End state is a real, offline-verifiable `.aep` evidence bundle — no UI clicks beyond the API key, no `curl`. See the AEP profile v1 spec (`docs/specs/aep-profile-v1.md`) for the manifest pattern design.

---

## Why this prototype exists

From a **PKI and trust-architecture perspective**, the interesting question is whether **high-risk AI obligations** (logging, transparency, robustness “in places”) can be **grounded in artefacts you already understand**: **CMS/CAdES-style or equivalent signing**, **[X.509](https://www.rfc-editor.org/rfc/rfc5280) path validation**, **revocation** ([OCSP](https://www.rfc-editor.org/rfc/rfc6960), [CRL](https://www.rfc-editor.org/rfc/rfc5280#section-5)), **TSA** ([RFC 3161](https://www.rfc-editor.org/rfc/rfc3161)), and **policy** aligned with **EN 319 102 / 401 / 411**—i.e. the same **trust-service** toolbox as under **[eIDAS](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910)**.

The **AI Act** (especially **Chapter III, Section 2**) frames _what_ deployers may need to show in terms of logging, transparency, oversight, and robustness. **This codebase** is an **implementation hypothesis** stated in **PKI terms**: bind agent outputs and sensitive **actions** to **signed, timestamped, verifiable evidence**, policy, and human steps—so **engineers and architects** can **inspect** the chain and **challenge the design**, not only read narrative mapping.

We deliberately map **[Article 10](https://artificialintelligenceact.eu/article/10/)** here to **integrity and provenance** (hashes, signatures, timestamps)—**not** to ML “data quality” as a PKI claim. In-app mapping: **`/trust/regulatory-mapping`**.

**MCP angle:** experimental **governance** next to identity ([MCP](https://modelcontextprotocol.io/)) and detection—see [mcp-ecosystem.md](docs/concepts/mcp-ecosystem.md).

---

## Core mapping (summary table)

_PKI-native summary: which AI Act articles we discuss against which **eIDAS / ETSI** levers, and what the repo actually runs. Full tables and sector matrix below._

| AI Act (navigator → EUR-Lex)                                                                                                                                                                                                  | Idea in this prototype                                                     | eIDAS / ETSI (entry points)                                                                                                                                                                                                                                                                                                                                                          | What the repo runs                                                                                                                                       |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [**Art. 10**](https://artificialintelligenceact.eu/article/10/) · [EUR-Lex context](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689)                                                                   | **Integrity & provenance** only—not ML dataset “quality” as a crypto claim | [eIDAS (EU) No 910/2014](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910) (trust services, e-signatures); [**EN 319 102-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31910201/), [**EN 319 132-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31913201/); [ETSI digital signatures](https://www.etsi.org/technologies/digital-signatures) | Canonical payloads, **signatures**, **Evidence Packages**                                                                                                |
| [**Art. 12**](https://artificialintelligenceact.eu/article/12/)                                                                                                                                                               | Tamper-evident trails, PKI-related events                                  | [**EN 319 401**](https://www.etsi.org/deliver/etsi_en/319400_319499/319401/), [**EN 319 411-1**](https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/)                                                                                                                                                                                                                       | **Audit ledger**, signed events, [**OCSP**](https://www.rfc-editor.org/rfc/rfc6960) / [**CRL**](https://www.rfc-editor.org/rfc/rfc5280) where configured |
| [**Art. 13**](https://artificialintelligenceact.eu/article/13/)                                                                                                                                                               | Verifiable crypto / policy state for deployers and auditors                | [eIDAS trust services — Commission overview](https://digital-strategy.ec.europa.eu/en/fact-pages/electronic-trust-services_en); [**EN 319 102-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31910201/), [**EN 319 412-1**](https://www.etsi.org/deliver/etsi_en/319400_319499/31941201/); [EU Digital Identity / eIDAS hub](https://eidas.ec.europa.eu/)                   | **Chain-of-trust validation**, verification UI/API                                                                                                       |
| [**Art. 6**](https://artificialintelligenceact.eu/article/6/) + [**Annex III**](https://artificialintelligenceact.eu/annex/3) · [Annex III (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) | Motivation when agents touch **high-risk** use types                       | Same stack as above                                                                                                                                                                                                                                                                                                                                                                  | Scenario docs, sector matrix—**not** a compliance certificate                                                                                            |

> **Focus:** cryptographic **integrity** and **provenance**, not ML **data quality** under the Act.

---

## What is implemented (prototype depth)

**PKI / crypto pipeline**

- **Digital signatures** over canonical content (RSA; optional [**ML-DSA**](https://csrc.nist.gov/publications/detail/fips/204/final) hybrid — [PQC plan](docs/developers/en/PLAN_PQC.md))
- **Certificate path validation** ([PKIX / X.509](https://www.rfc-editor.org/rfc/rfc5280)) and QTSP-oriented trust configuration (**deployment-dependent**)
- [**RFC 3161**](https://www.rfc-editor.org/rfc/rfc3161) timestamping (real or mock TSA)
- **Hash-chained audit** events; signing where enabled
- **Evidence Packages** (`.aep`): export + **offline** verification (JAR/scripts in repo)
- **Spring Boot** + **Next.js**; REST + partner/MCP-style **governed actions** and attestation flows

**Two signing modes** (see [`docs/concepts/signing-modes.md`](docs/concepts/signing-modes.md) for the full decision tree):

- **sign mode** — `POST /api/sign`. Tenant API key only; `agentId`
  optional. For integrity-only use cases: publication signing,
  CI/CD artefacts, internal audit logs. Helps discharge AI Act
  Article 12.
- **attest mode** — `POST /api/v1/attest`. Requires registered
  agent + action_type + policy. Returns same crypto envelope plus
  per-rule policy coverage report. For high-risk AI outputs under
  Annex III. Helps discharge AI Act Articles 12 + 13 + 14.

Both modes share the same cryptographic substrate (canonicalise →
SHA-256 → hybrid RSA-4096 + ML-DSA-65 → RFC 3161 timestamp). They
differ in the attribution and policy evaluation layered on top.
Machine-readable description at `GET /api/public/signing-modes`.

Technical entry: [docs/README.md](docs/README.md).

---

## Post-quantum cryptography (PQC)

- Dual-signing: RSA-4096 + **ML-DSA-65** ([NIST PQC project / Dilithium](https://csrc.nist.gov/projects/post-quantum-cryptography))
- Bouncy Castle BCPQC; [strategy doc](docs/developers/en/PLAN_PQC.md) · `GET /api/v1/crypto/health`

---

## Additional prototype components

- **Delegation chain modelling** — [delegation builder](docs/features/delegation-builder.md), [concepts](docs/knowledgebase/understanding_delegation_chains.md), `/delegation-chains/builder`
- **Human-in-the-loop** — approvals / review queues (demo tenants)
- **Policy-gated actions** — illustrative policies only (**not** legal compliance)

---

## Deep dive — regulatory mapping (engineering argument, not legal canon)

**PKI lens:** the tables below are for **mapping conversations**—they do **not** replace **CP/CPS** discipline or notified-body work. **Not legal advice.** Counsel validates classifications. Extended analysis: [eu_ai_act_multi_sector_opportunities.md](docs/vision/eu_ai_act_multi_sector_opportunities.md).

### Speaking lines (hypothesis, not statutory interpretation)

- The **AI Act** frames _what_ trust and traceability may be required in places; **eIDAS / ETSI** show _how_ the EU often implements **integrity and validation** in practice—this prototype **tests alignment in software**.
- **Article 10** in _this_ mapping means **integrity & provenance**—not ML training-data “quality” as a PKI deliverable.

### Three-column mental model (EN)

| EU AI Act                                                                                                                    | eIDAS / ETSI                                                                                                                                                                                                                                                                         | Aletheia (prototype)                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [**Art. 6**](https://artificialintelligenceact.eu/article/6/) — high-risk AI systems                                         | [Trust services](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910); CA / TSP / [QTSP (Commission)](https://digital-strategy.ec.europa.eu/en/fact-pages/qualified-trust-service-providers-qttsp_en)                                                             | End-to-end **PKI path**: CA material, **validation**, cross-border **trust-service** practice per [eIDAS hub](https://eidas.ec.europa.eu/) |
| [**Art. 10**](https://artificialintelligenceact.eu/article/10/) — data integrity & provenance (_not_ “quality” on this axis) | [eIDAS](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910) e-signatures (integrity + authenticity)                                                                                                                                                              | Signed artefacts; integrity checks                                                                                                         |
| [**Art. 12**](https://artificialintelligenceact.eu/article/12/) — logging, traceability                                      | Non-repudiation; [**EN 319 401**](https://www.etsi.org/deliver/etsi_en/319400_319499/319401/), [**EN 319 411-1**](https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/)                                                                                                      | Serials; [OCSP](https://www.rfc-editor.org/rfc/rfc6960) / [CRL](https://www.rfc-editor.org/rfc/rfc5280); validation history                |
| [**Art. 13**](https://artificialintelligenceact.eu/article/13/) — transparency (verifiability)                               | [**EN 319 102-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31910201/); [electronic trust services (EU)](https://digital-strategy.ec.europa.eu/en/fact-pages/electronic-trust-services_en)                                                                                 | Chain validation; **source / anchor verification**                                                                                         |
| [**Art. 14**](https://artificialintelligenceact.eu/article/14/) — human oversight                                            | _Indirect:_ [qualified trust services](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910) + audit trails → **accountability**; human control remains **process**                                                                                                | Validation + audit **evidence** for reviewers—not a substitute for governance                                                              |
| Reliability / future                                                                                                         | [eIDAS 2.0 — (EU) 2024/1183](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1183); [EU eIDAS policy](https://digital-strategy.ec.europa.eu/en/policies/eidas-regulation); [ETSI quantum-safe crypto](https://www.etsi.org/technologies/quantum-safe-cryptography) | Hybrid RSA + ML-DSA; [PoC PQC](docs/developers/en/PLAN_PQC.md)                                                                             |

### Full layer mapping (EU AI Act → eIDAS/ETSI → prototype)

| Layer                            | EU AI Act                                                                                                                                        | → eIDAS / ETSI                                                                                                                                                                                                                                                              | → Aletheia (prototype)                                                    | One-liner (EN)                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Data integrity & provenance**  | [**Art. 10**](https://artificialintelligenceact.eu/article/10/) — scope here: integrity + provenance; “data quality” in the Act ≠ this PKI slice | [eIDAS](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910); [**EN 319 102-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31910201/), [**EN 319 132-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31913201/)                         | Signed artefacts                                                          | Art. 10 → integrity & provenance via signatures; **not** an ML data-quality claim.           |
| **Traceability & logging**       | [**Art. 12**](https://artificialintelligenceact.eu/article/12/)                                                                                  | [**EN 319 401**](https://www.etsi.org/deliver/etsi_en/319400_319499/319401/), [**EN 319 411-1**](https://www.etsi.org/deliver/etsi_en/319400_319499/31941101/)                                                                                                              | OCSP/CRL; audit                                                           | Art. 12 → PKI-anchored traceability.                                                         |
| **Transparency & verifiability** | [**Art. 13**](https://artificialintelligenceact.eu/article/13/)                                                                                  | [**EN 319 102-1**](https://www.etsi.org/deliver/etsi_en/319100_319199/31910201/), [**EN 319 412-1**](https://www.etsi.org/deliver/etsi_en/319400_319499/31941201/); [trust services (EU)](https://digital-strategy.ec.europa.eu/en/fact-pages/electronic-trust-services_en) | Path validation; root / policy provenance                                 | Art. 13 → cryptographic verifiability.                                                       |
| **Human oversight (supporting)** | [**Art. 14**](https://artificialintelligenceact.eu/article/14/) (_indirect_)                                                                     | [eIDAS trust stack](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910); audit-friendly logs                                                                                                                                                            | Evidence for review                                                       | Art. 14 → PKI does not add the human; it makes outcomes **reviewable** and **attributable**. |
| **High-risk trust architecture** | [**Art. 6**](https://artificialintelligenceact.eu/article/6/)                                                                                    | CA, TSP, [QTSP](https://digital-strategy.ec.europa.eu/en/fact-pages/qualified-trust-service-providers-qttsp_en); [**EN 319 401**](https://www.etsi.org/deliver/etsi_en/319400_319499/319401/)                                                                               | Configurable trust material + validation + verification UX                | Strong trust layer **analogous** to regulated PKI—**prototype**, not a national scheme.      |
| **Crypto agility / PQC**         | High-risk chapter context ([Arts 9–15 navigator](https://artificialintelligenceact.eu/section/3-2/))                                             | EU / [ETSI quantum-safe](https://www.etsi.org/technologies/quantum-safe-cryptography)                                                                                                                                                                                       | Hybrid [ML-DSA](https://csrc.nist.gov/publications/detail/fips/204/final) | Future-proofing—**not** a claim that the Act mandates PQC.                                   |

### Official & secondary anchors

| Resource                             | URL                                                                                                                    |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **AI Act (EU law)**                  | [EUR-Lex CELEX 32024R1689](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689)                     |
| **AI Act — implementation timeline** | [Commission AI Act Service Desk](https://ai-act-service-desk.ec.europa.eu/en/ai-act/eu-ai-act-implementation-timeline) |
| **Navigator — Annex III**            | [artificialintelligenceact.eu/annex/3](https://artificialintelligenceact.eu/annex/3)                                   |
| **Navigator — Arts 9–15**            | [Section 3(2) high-risk](https://artificialintelligenceact.eu/section/3-2/)                                            |
| **Deployer — Art. 26**               | [navigator](https://artificialintelligenceact.eu/article/26/)                                                          |
| **FRIA — Art. 27**                   | [navigator](https://artificialintelligenceact.eu/article/27/)                                                          |
| **eIDAS (2014)**                     | [EUR-Lex 910/2014](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32014R0910)                             |
| **eIDAS 2.0 (2024/1183)**            | [EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1183)                                      |

### High-risk chapter — article quick map (prototype levers)

| Article | Navigator                                                   | Gist                      | Prototype lever                          |
| ------- | ----------------------------------------------------------- | ------------------------- | ---------------------------------------- |
| **9**   | [Art. 9](https://artificialintelligenceact.eu/article/9/)   | Risk management           | Policies, kill-switch, delegation limits |
| **10**  | [Art. 10](https://artificialintelligenceact.eu/article/10/) | Data governance           | _Here:_ integrity/provenance via crypto  |
| **11**  | [Art. 11](https://artificialintelligenceact.eu/article/11/) | Technical documentation   | Exports, metadata                        |
| **12**  | [Art. 12](https://artificialintelligenceact.eu/article/12/) | Record-keeping            | Hash-chained audit, signed events        |
| **13**  | [Art. 13](https://artificialintelligenceact.eu/article/13/) | Transparency to deployers | Agent identity / capabilities in UI/API  |
| **14**  | [Art. 14](https://artificialintelligenceact.eu/article/14/) | Human oversight           | Approvals, escalation                    |
| **15**  | [Art. 15](https://artificialintelligenceact.eu/article/15/) | Robustness / security     | Verification endpoints, signals          |

**Deployer discussion only:** [Art. 26](https://artificialintelligenceact.eu/article/26/), [Art. 27](https://artificialintelligenceact.eu/article/27/) — not a claim this repo satisfies them.

### Annex III → sectors (condensed)

High-risk categories under [**Art. 6(2)**](https://artificialintelligenceact.eu/article/6/) — see [Annex III navigator](https://artificialintelligenceact.eu/annex/3) and [EUR-Lex Annex III](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689): (1) Biometrics, (2) Critical infrastructure, (3) Education, (4) Employment, (5) Essential services & benefits, (6) Law enforcement, (7) Migration/border, (8) Justice & democratic processes.

### Sector matrix (illustrative — not classification advice)

| Sector                           | Typical agentic actions    | Touchpoints (links)                                                                                                                                                                                                                                                                                            | Prototype-style response                                                                                              |
| -------------------------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Healthcare**                   | Triage, notes, orders      | [Annex III(5)(d)](https://artificialintelligenceact.eu/annex/3); [MDR](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32017R0745); [IVDR](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32017R0746); [GDPR](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679) | Human gate; signed evidence; audit                                                                                    |
| **Life & health insurance**      | Underwriting, claims       | [Annex III(5)(c)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                | Human binds; policies                                                                                                 |
| **Banking & credit**             | Credit, KYC                | [Annex III(5)(b)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                | Threshold approval; exports                                                                                           |
| **Payments & treasury**          | Pay, FX                    | [PSD2](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32015L2366); [AML overview (Commission)](https://finance.ec.europa.eu/financial-crime/anti-money-laundering-and-countering-financing-terrorism_en); AI Act if **5(b)**                                                                      | Governance gate; demo **PaymentIntent**                                                                               |
| **Legal & dispute**              | Drafts, discovery          | [Annex III(8)(a)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                | Delegation; human sign-off · **[OpenCourt](docs/vision/scenarios/opencourt.md)**                                      |
| **HR & talent**                  | Screening                  | [Annex III(4)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                   | Escalation; audit                                                                                                     |
| **Education**                    | Grading                    | [Annex III(3)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                   | Roles; review · **[School Compass](docs/vision/scenarios/school-compass.md)**                                         |
| **Critical infrastructure**      | Control suggestions        | [Annex III(2)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                   | Dual-control patterns                                                                                                 |
| **Public benefits**              | Eligibility                | [Annex III(5)(a)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                | Records; FRIA-aware design · **[Bürokratt Kit](docs/vision/scenarios/burokratt-kit.md)**                              |
| **Law enforcement**              | Case support               | [Annex III(6)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                   | Sensitive; audit narrative only where appropriate                                                                     |
| **Migration & border**           | Checks                     | [Annex III(7)](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                                                                                   | High sensitivity                                                                                                      |
| **Political / civic**            | Targeting                  | [Annex III(8)(b)](https://artificialintelligenceact.eu/annex/3); [GPAI — navigator](https://artificialintelligenceact.eu/section/4/)                                                                                                                                                                           | Demo boundaries                                                                                                       |
| **Biometric / emotion**          | Inference                  | [**Art. 5**](https://artificialintelligenceact.eu/article/5/) · [Annex III](https://artificialintelligenceact.eu/annex/3)                                                                                                                                                                                      | Default off; legal review                                                                                             |
| **Citizen × AI (cross-cutting)** | Personal AI accountability | [Art. 14](https://artificialintelligenceact.eu/article/14/); [eIDAS 2.0](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1183)                                                                                                                                                               | EUDI Wallet × EATF; Verifiable Credential receipt · **[Citizen Receipts](docs/vision/scenarios/citizen-receipts.md)** |

---

## Documentation

| You are…                                      | Start here                                                                                                                                                                                                                            |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Operator / buyer**                          | [Product and trust overview](docs/README.md#operator--buyer)                                                                                                                                                                          |
| **Developer / integrator**                    | [API, setup, and integration](docs/README.md#developer--integrator)                                                                                                                                                                   |
| **Partner / implementation lead**             | [Partner integrations](docs/README.md#partner--implementation)                                                                                                                                                                        |
| **Product IA / route ownership**              | [Route governance](docs/developers/en/route-governance.md) · [Navigation IA](docs/developers/en/navigation-ia.md)                                                                                                                     |
| **Delegation UI**                             | [Builder quick start](docs/features/delegation-builder.md#quick-start)                                                                                                                                                                |
| **Research (Article 01 plan & bibliography)** | [docs/research/README.md](docs/research/README.md)                                                                                                                                                                                    |
| **Reference scenarios (4)**                   | [OpenCourt](docs/vision/scenarios/opencourt.md) · [Bürokratt Kit](docs/vision/scenarios/burokratt-kit.md) · [School Compass](docs/vision/scenarios/school-compass.md) · [Citizen Receipts](docs/vision/scenarios/citizen-receipts.md) |
| **Open Kratt manifest spec**                  | [docs/specs/kratt-manifest.md](docs/specs/kratt-manifest.md) · [JSON Schema](docs/specs/kratt-manifest.schema.json)                                                                                                                   |
| **RIA / Bürokratt pilot pitch**               | [docs/partners/ria-pilot.md](docs/partners/ria-pilot.md)                                                                                                                                                                              |

Full index: [docs/README.md](docs/README.md).

---

## Quick start

```bash
git clone https://github.com/tyche-institute/eatf.git && cd eatf
cp .env.example .env
openssl genpkey -algorithm RSA -out ai.key -pkeyopt rsa_keygen_bits:4096
# In .env set: AI_ALETHEIA_SIGNING_KEY_PATH=./ai.key
```

```bash
cd backend && ./mvnw spring-boot:run
```

```bash
cd frontend && cp .env.example .env.local && npm install && npm run dev
```

- Backend: http://localhost:8081
- Frontend: http://localhost:3000
- Set `OPENAI_API_KEY` in `.env` for the AI demo. Set `NEXT_PUBLIC_API_URL` to your backend URL in `frontend/.env.local`.

More: [docs/README.md](docs/README.md) → Developers.

---

## Demo accounts (development mode)

`demo@aletheia.ai` / `Demo123!` — **tenant-scoped ADMIN** on each of **demo-healthcare**, **demo-fintech**, **demo-legal** (one membership row per tenant). NOT SUPER_ADMIN — V208 migration intentionally downgraded this account because SUPER_ADMIN combined with X-Tenant-Id pivoting under the `demo` profile enabled cross-tenant access. See [`backend/.../db/seeding/DemoBaselineRecovery.java`](backend/src/main/java/ai/aletheia/db/seeding/DemoBaselineRecovery.java) and [`DemoBaselineRecoveryTest.java`](backend/src/test/java/ai/aletheia/db/seeding/DemoBaselineRecoveryTest.java) for the guard. Per-tenant admins: `admin@demo-{healthcare,fintech,legal}.local` / `Demo123!`. Full detail: [database seeding](docs/developers/en/database-seeding.md).

---

## License

MIT. See [LICENSE](LICENSE). Authorship: [docs/README.md#authorship](docs/README.md#authorship).

---

_Validate legal URLs against your source of record. This README is the **canonical project pitch** for the repository._
