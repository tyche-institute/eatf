---
title: "OVERT Level 2 Agentic Control Mapping"
description: "Control-by-control draft mapping for the first EATF OVERT scope: MCP tools/call attestation."
audience: ["developers", "partners"]
tags: ["overt", "controls", "mcp", "attestation"]
last_updated: "2026-05-14"
---

# OVERT Level 2 Agentic Control Mapping

Status: internal draft. This is not a public OVERT conformance claim.

## TLDR

The first defensible scope is still narrow:

```text
OVERT 1.0 Level 2 Agentic-Extended readiness for MCP tools/call
attestation through @eatf/mcp-gateway and EATF .aep evidence packages.
```

The current implementation is strongest in ATTEST, temporal binding, package
verification, and auditability. It is not ready for Level 3/4 statistical or
evidence-grade claims. It also should not claim whole-platform OVERT
conformance.

## Scope Boundary

In scope:

- registered EATF tenant-bound agents;
- `@eatf/mcp-gateway` observing MCP `tools/call` calls;
- `EATF_ATTEST_MODE=attest` and `POST /api/v1/attest`;
- OVERT-profiled `.aep` packages with `overt_receipt.json`;
- Java verifier as the authoritative verifier;
- TypeScript verifier as an alpha convenience verifier.

Out of scope:

- model training, fine-tuning, and dataset lineage;
- non-MCP execution paths;
- streaming chunk-chain claims;
- full Level 3 statistical sampling;
- Level 4 evidence-grade preservation and portability rehearsal;
- legal admissibility or regulatory approval conclusions.

## Domain Mapping

| OVERT control area | Requirement intent | EATF evidence | Status | Gap / assessor question |
|---|---|---|---:|---|
| GOV-1 Governance policy | Document who owns runtime attestation controls and release gates. | TSPS, release checklist, readiness docs | Partial | Need explicit OVERT owner/RACI and approval gate before public claim. |
| GOV-2 Scope declaration | State exact system boundary, exclusions, maturity level, and profile. | This document, profile submission pack | Ready for review | External reviewer must confirm scope language is narrow enough. |
| GOV-3 Change management | Changes to profile/verifier/key behavior must be reviewed. | Release checklist, verifier tests | Partial | Add OVERT-specific release checklist row before claim. |
| IDE-1 System inventory | Identify assessed agents, interfaces, risk class, and protocols. | Agent registry, Kratt manifest, MCP profile | Partial | Need one exported sample agent manifest in the review packet. |
| IDE-2 Tenant-bound identity | Bind attestations to tenant and agent identity. | Tenant-bound URNs, `metadata.agent_id`, `overt_receipt.subject` | Partial | Sign-mode packages can have null agent; first claim must require MCP attest-mode agent id. |
| IDE-3 Risk classification | Classify in-scope agent/tool actions. | Agent registration risk fields, policy registry | Partial | Map EATF risk classes to OVERT scope terms. |
| PRO-1 Runtime policy enforcement | Policy must execute at runtime boundary. | `AtapPolicyEvaluationService`, MCP gateway attest mode | Partial | Transparent proxy currently observes post-response; irreversible actions need server-mode/pre-dispatch enforcement. |
| PRO-2 Privacy by architecture | Protected content should not leave operator environment. | `privacyMode`, hash-only attest path, OVERT receipt hash binding | Partial | Need operator guide showing privacy-mode default for governed MCP flows. |
| PRO-3 Non-egress controls | Declare and enforce egress path for receipts. | Gateway config, backend `/api/v1/attest` endpoint | Early | Need certificate pinning / endpoint pin set if pursuing higher AAL. |
| ATT-1 Receipt generation | Every in-scope runtime action emits a verifiable receipt. | `.aep`, `overt_receipt.json`, MCP fixture | Partial | Need CI coverage that every successful MCP tools/call creates a fixture-equivalent record. |
| ATT-2 Cryptographic binding | Bind payload/canonical bytes, hash, signature, timestamp, and receipt. | `hash.sha256`, RSA, optional ML-DSA, RFC 3161, Java verifier | Strong | Current TS verifier has compatibility exceptions; Java remains authoritative. |
| ATT-3 Witness independence | IAP must be structurally independent from assessed operator. | IAP operating pack | Partial | Needs signed independence declaration per pilot/operator. |
| ATT-4 Transparency logs | Publish digest/ledger data for auditor replay. | Hash-chained ledger, trust-anchor docs | Partial | Need export sample for the exact first scope. |
| ATT-5 Verifier reproducibility | Independent auditor can reproduce pass/fail on fixtures. | Java verifier tests, valid/tampered fixtures | Ready | Add assessor instructions with exact commands and checksums before sending. |
| MEA-1 Coverage measurement | Report which policies/rules were evaluated. | `policy_coverage`, policy rule results | Partial | Need stable denominator for MCP policies. |
| MEA-2 Statistical rigor | Safety claims need sample sizes/confidence intervals. | Not in first scope | Out | Explicitly exclude Level 3 statistical claims. |
| RES-1 Incident response | Integrity-impacting incidents must have disclosure path. | IAP operating pack, external review pack | Partial | Need public vulnerability intake and 72-hour disclosure procedure. |
| RES-2 Portability | Operator can move historical evidence to another IAP. | Portability escrow outline | Early | Need JSON schema and sample export. |
| AGT-1 Tool-call governance | Agentic tool calls are observed and policy-evaluated. | MCP profile, gateway, MCP `.aep` fixture | Partial | Need live end-to-end demo script with backend-generated attestation id. |
| AGT-2 MCP server trust | Gateway records tool identity and request/response metadata. | MCP profile canonical fields | Partial | Need trust model for upstream MCP server identity. |
| AGT-3 Human oversight | Human-in-the-loop actions are evidenced when invoked. | Human review metadata and policy service | Out for first claim | Exclude unless the specific pilot flow requires it. |
| AGT-4 Delegation chains | Multi-agent delegation is recorded and replayable. | Delegation chain docs | Out for first claim | Defer to future Agentic-Extended scope. |
| AGT-5 Persistent state governance | Durable agent state is governed and drift-detected. | No first-scope artifact | Out | Exclude from first claim. |

## Claim Readiness

| Claim | Current posture |
|---|---|
| OVERT-aligned | Defensible for public copy. |
| Level 1 self-assessed, narrow MCP scope | Plausible after reviewer packet is complete. |
| Level 2 Agentic-Extended, narrow MCP scope | Candidate target for external pre-review. |
| Level 3 | Not ready; statistical rigor missing. |
| Level 4 | Not ready; evidence-grade portability, t-of-n notary, and annual rehearsal missing. |
| Whole-platform OVERT conformance | Not supportable. |

## Required Before External Send

- Include the MCP `tools/call` valid and denied-policy fixtures.
- Include exact verifier commands and expected results.
- Freeze safe claim language: "OVERT-aligned; conformance work in progress."
- Add an operator-specific independence declaration when a pilot partner is
  known.
