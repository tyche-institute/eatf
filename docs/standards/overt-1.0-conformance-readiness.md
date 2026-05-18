---
title: "OVERT 1.0 Conformance Readiness"
description: "Internal gap matrix and action plan for EATF alignment with OVERT 1.0."
audience: ["developers", "partners"]
tags: ["overt", "standards", "attestation", "conformance"]
last_updated: "2026-05-14"
---

# OVERT 1.0 Conformance Readiness

Status: internal working document. This is not a public conformance claim.

OVERT 1.0 is currently stable at version `1.0.0`, released 2026-03-25. The
public EATF stance remains: **OVERT-aligned; conformance work in progress**.

## TLDR

EATF already implements the core evidence shape OVERT asks for: signed runtime
records, tenant-bound agent identity, `.aep` evidence packages, offline
verification, timestamping, PQC metadata, and a hash-chained ledger.

The next defensible target is a narrow, assessed claim around MCP tool-call
attestation, not whole-platform conformance. Candidate target:

```text
OVERT Level 2 Agentic-Extended readiness, scoped to MCP tools/call
attestation through @eatf/mcp-gateway and EATF .aep evidence packages.
```

Do not publish that as a conformance claim until the profile, evidence samples,
IAP operating pack, and external assessment path are ready.

## First Scope

The first claim should cover only this bounded workflow:

1. A registered tenant-bound agent uses `@eatf/mcp-gateway`.
2. The gateway observes an MCP `tools/call` request and response.
3. The gateway sends a policy-selected `AttestationRequest` to
   `POST /api/v1/attest` in `EATF_ATTEST_MODE=attest`.
4. The backend evaluates policy, signs the canonical record, anchors time, and
   persists the attestation.
5. The relying party verifies the evidence package or attestation record
   independently.

Out of scope for the first claim:

- model training, fine-tuning, dataset lineage, and model evaluation;
- all non-MCP agent execution paths;
- human-review workflows not invoked by the attested action;
- full Level 3 statistical measurement and Level 4 evidence-grade preservation;
- legal compliance, regulatory approval, or admissibility conclusions.

## Draft Claim Language

Use only internally until external review:

```text
EATF is preparing an OVERT 1.0 Level 2 Agentic-Extended claim for MCP
tools/call attestation, using the EATF AEP Profile v1 and MCP Attestation
Profile v1 as the candidate protocol profile. Scope summary: registered
tenant-bound EATF agents invoking MCP tools through @eatf/mcp-gateway over
stdio, with attest-mode records persisted by POST /api/v1/attest. Exclusions:
non-MCP agent actions, streaming chunks, pre-dispatch side-effect blocking in
transparent proxy mode, training-time controls, and platform SDLC controls.
```

Public wording remains shorter:

```text
OVERT-aligned. Conformance work in progress.
```

## Execution Progress Matrix

Last updated: 2026-05-14.

This matrix is the working tracker for what is done, what is blocked, and what
we do next. It should be updated before any release, public standards-page
change, external review send, or OVERT submission.

| Workstream | Current status | Evidence / artifact | Next move | Owner | Gate |
|---|---|---|---|---|---|
| OVERT source/version tracking | Ready | OVERT `1.0.0` recorded here; version feed documented | Re-check `https://overt.is/latest.json` before external send and every release | maintainer | Latest version confirmed in release/submission notes |
| Scope and claim language | Ready for external review | First-scope section, draft claim language, Level 2 mapping | Ask reviewer to confirm the MCP-only scope is narrow enough | maintainer + reviewer | Reviewer confirms wording in writing |
| Public wording | Safe | Public copy limited to "OVERT-aligned; conformance work in progress" | Keep this language until review/submission path closes | docs/marketing owner | No public "conformant", "certified", or "approved" wording |
| AEP OVERT receipt profile | Implemented; pre-review ready | `docs/specs/aep-profile-v1.md`, `overt_receipt.json`, Java/TS verifier checks | Freeze receipt schema for the reviewed commit or release tag | maintainer | Reviewed tag contains exact schema and fixture set |
| MCP `tools/call` evidence scope | Implemented; pre-review ready | `mcp-tools-call-valid.aep`, `mcp-tools-call-denied-policy.aep`, MCP profile docs | Add recurring CI check for the OVERT fixture verification command | backend maintainer | CI blocks regressions in MCP OVERT fixtures |
| Java verifier | Authoritative for review | `OvertFixtureVerificationTest`, `EvidenceVerifierImpl` | Use Java verifier as the required assessor command | backend maintainer | All OVERT fixture tests pass on reviewed commit |
| TypeScript verifier | Passing convenience verifier; alpha for OVERT | `sdks/eatf-verifier-ts/src/overt.ts`, TS fixture tests | Keep as secondary evidence; document TSA/browser limitations | SDK maintainer | TS build/test pass; limitations stay explicit |
| Browser/WASM verification path | Not first-scope blocker | Frontend verifier docs and current exclusion | Either finish trust-chain path or explicitly exclude it from first claim | frontend maintainer | Decision recorded before formal submission |
| IAP independence and operations | In progress | IAP operating pack, external review pack | Add named owner/RACI and pilot-specific independence declaration | ops/legal owner | Independence statement ready for selected pilot/reviewer |
| External pre-review | Packet ready; not sent | Pre-review packet, feedback register, submission decision record | Select named reviewer or pilot auditor and send the packet | founder/maintainer | Reviewer receives packet and feedback register is updated |
| Review remediation | Waiting on external findings | Feedback register with internal dry-run findings | Convert every reviewer comment into a register row; close blocker/major findings | maintainer | No open blocker; major findings closed or excluded |
| Formal OVERT profile submission | Deferred | Submission decision record | After clean pre-review, decide Level 1 self-assessed vs Level 2 submission route | maintainer | Reviewed tag, no open blocker/major, current OVERT contact verified |
| Level 3 / Level 4 work | Out of current scope | Gap matrix exclusions | Design sampling denominator, portability escrow, and preservation proof later | standards owner | Separate roadmap approved; not mixed into first claim |

## Immediate Next Actions

1. Select one external reviewer or pilot auditor for the MCP `tools/call`
   scope.
2. Send `docs/standards/overt-external-pre-review-packet.md` plus the listed
   attachments.
3. Record every comment in
   `docs/standards/overt-review-feedback-register.md`.
4. Fix or explicitly exclude all blocker and major findings.
5. Freeze a reviewed commit or release tag and re-run the Java and TypeScript
   fixture verification commands.
6. Decide whether the first public route is a narrow Level 1 self-assessment or
   a Level 2 Agentic-Extended submission.

## Gap Matrix

| OVERT area | EATF artifact | Status | Gap | Next action |
|---|---|---:|---|---|
| Published standard/version tracking | `/standards`, this document | Ready | Need recurring version check | Track `https://overt.is/latest.json` before each release |
| Attestation by construction | `POST /api/sign`, `POST /api/v1/attest`, MCP gateway | Partial | Proxy attest mode was post-response; no streaming chunk chain | Keep sign/attest modes distinct; add streaming hash chain in Phase 2 v0.2 |
| Privacy by architecture | `.aep` metadata, hashed tenant id, attest `privacyMode` | Partial | Some sign-mode payloads can still contain raw text by design | Default governed MCP attest mode to `privacyMode=true`; document hash/tokenize best practice |
| Independence by structure | Tenant-bound URNs, IAP role docs | Partial | Need operating proof of structural independence from assessed operators | Publish IAP operating pack and relationship disclosures |
| Statistical rigor | Policy coverage fields, reports | Early | No OVERT Level 3 sampling methodology yet | Defer Level 3; design coverage denominator and sampling proof later |
| Open by design | Public specs, verifier, CLI, profile drafts | Partial | OVERT profile registration not attempted | Prepare profile submission package after the v1 draft comment period |
| Security-supporting evidence | MCP gateway, policy engine, audit events, ledger | Partial | Transparent proxy cannot block side effects before response | Use server-mode before-action attestation for irreversible actions; add pre-dispatch proxy policy |
| Foundations / AAL | `.aep` signatures, TSA, ledger, offline verifier | AAL-2/3 shaped | AAL mapping not formally stated per evidence path | Add AAL column to profile test vectors and verifier reports |
| GOVERN domain | TSPS, release checklist, policy registry, OVERT mapping | Partial | OVERT owner/RACI still needs a release gate | Add OVERT-specific release checklist row before claim |
| IDENTIFY domain | agent registry, manifests, risk classification | Partial | Risk taxonomy not OVERT-specific | Map manifest fields to OVERT scope and risk inventory |
| PROTECT domain | policy engine, action requests, kill switch | Partial | Runtime controls vary by flow | Constrain first claim to MCP `tools/call` and registered policy |
| ATTEST domain | evidence package, signatures, timestamp, verifier | Strong | Browser full TSA chain validation not complete | Keep Java verifier authoritative; finish WASM trust-chain path |
| MEASURE domain | policy coverage, analytics | Early | No confidence intervals / reproducible sampling | Out of first claim; future Level 3 work |
| RESPOND domain | incident/disclosure docs, webhooks | Partial | OVERT response-action evidence not mapped | Include incident and portability procedures in IAP pack |
| Agentic controls | MCP gateway profile, delegation docs | Partial | Durable state and identity-chain controls not fully assessed | Agentic-Extended only for MCP path with explicit exclusions |
| Non-egress architecture | privacy mode, hashed inputs/outputs | Partial | Need operator-facing configuration proof | Add verifier-visible privacy mode metadata in later `.aep` revision |
| Temporal binding | RFC 3161 timestamping, TSA trust store | Partial | Qualified TSA partnership pending | Maintain internal TSA for pilots; prepare qualified-TSA swap-in |
| Third-party auditability | offline Java verifier, TS verifier alpha | Partial | TS verifier still has TSA limitations | Treat Java verifier as authoritative for assessment |
| Legal preservation | termination plan, public-key mirror | Partial | Portability escrow export format incomplete | Publish IAP portability escrow format |
| Protocol profile registry | AEP + MCP profile drafts, submission pack | Pre-review ready | Not submitted/registered | Run external pre-review before formal submission |
| IAP qualification | IAP operating pack | In progress | Needs publication, metrics, ownership disclosures | Complete and publish operating pack before claim |
| Qualified assessor | External review pack | Not ready | No assessor selected | Prepare assessor packet and evidence samples |

## 30 / 60 / 90 Plan

Next 30 days:

- keep all public copy on "OVERT-aligned" language;
- maintain the OVERT control-by-control matrix for Level 2 Agentic-Extended;
- publish or stage the IAP operating pack;
- keep the MCP attest-mode valid and denied-policy `.aep` samples passing;
- add CI checks that verify those samples with the Java verifier.

Next 60 days:

- finish browser/WASM trust-chain validation or explicitly exclude it;
- add profile test vectors for AEP and MCP attest-mode;
- add a machine-readable scope statement for the first claim;
- prepare profile registry submission materials.

Next 90 days:

- submit or self-declare the protocol profile according to OVERT registry rules;
- run an external pre-assessment against the first scope;
- decide whether the first public claim is Level 1 or Level 2 based on the
  assessor feedback.

## Sources

- OVERT 1.0: `https://overt.is/`
- OVERT version feed: `https://overt.is/latest.json`
- OVERT IPR policy: `https://overt.is/ipr-policy`
- EU AI Act: `https://eur-lex.europa.eu/eli/reg/2024/1689/oj`
- NIST AI RMF 1.0: `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10`
