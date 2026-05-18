---
title: "OVERT IAP Operating Pack"
description: "Operating-policy pack required before EATF can support a formal OVERT Independent Attestation Provider claim."
audience: ["developers", "partners"]
tags: ["overt", "iap", "operations", "attestation"]
last_updated: "2026-05-14"
---

# OVERT IAP Operating Pack

Status: draft. This pack supports readiness work only; it is not a public
OVERT conformance assertion.

## Purpose

OVERT treats an Independent Attestation Provider (IAP) as the party that is
structurally independent from the AI system operator, validates attestations,
and makes audit material available to relying parties.

For EATF, the IAP role applies when EATF validates or preserves attestations for
another operator's AI system. It does not apply when EATF is merely producing
self-contained demo evidence for its own demo surface.

## Operating Commitments

EATF should be able to show the following before making any formal IAP claim.

| Area | Commitment | Required artifact |
|---|---|---|
| Structural independence | EATF is not controlled by the assessed operator and does not share management with it | Independence declaration per operator |
| Contractual independence | Operator cannot suppress, modify, or delay attestation artifacts unilaterally | Customer terms / attestation addendum |
| Relationship disclosure | Material business relationships are disclosed to relying parties where relevant | Relationship disclosure template |
| Ownership disclosure | Beneficial ownership can be disclosed to assessed operators on request | Ownership disclosure procedure |
| Uptime transparency | Notary/API availability is measured and publishable | Monthly uptime metric export |
| Auditor access | Epoch data, digest ledgers, public keys, and evidence samples can be produced | Auditor access runbook |
| Key management | Signing keys, PQC keys, rotation, and revocation are documented | Key-management practice statement |
| Incident disclosure | Integrity-impacting incidents have a 72-hour disclosure path | Incident disclosure runbook |
| Annual transparency | Volume, verification failures, and integrity incidents are summarized yearly | Transparency report template |
| Portability | Operators can move to another IAP without losing historical evidence | Portability escrow format |
| Migration rehearsal | Level 4 candidates can rehearse portability annually | Rehearsal checklist |

## Publication Set

The minimum public or customer-shareable set:

1. IAP operating policy.
2. Key-management practice statement.
3. Incident disclosure and vulnerability intake policy.
4. Portability escrow format.
5. Transparency report template.
6. Auditor access runbook.
7. OVERT scope statement for each assessed deployment.

Keep commercial terms separate. The operating pack should describe evidence
rights and verification behavior, not pricing or sales process.

## IAP Scope Statement Template

```text
IAP scope:
  operator:
  tenant:
  systems:
  agent identifiers:
  interfaces:
  traffic classes:
  policy ids and versions:
  evidence package profile:
  verifier version:
  trust anchors:
  start:
  end:
  exclusions:
  operator-declared dependencies:
  EATF-controlled dependencies:
```

The scope statement must be specific enough that an auditor can tell what was
inside and outside the attested boundary. Generic phrases such as "all AI
activity" are not acceptable.

## Key Management

Required before public IAP posture:

- maintain active and retired signing key identifiers;
- publish the public-key history mirror;
- document RSA and ML-DSA key generation, activation, rotation, revocation, and
  archival;
- define who can authorize key changes;
- separate demo/test keys from production keys;
- record which key signed each evidence package and ledger block.

Current implementation hooks already exist for RSA/PQC key ids on evidence and
ledger records. The missing operating layer is publication discipline and
periodic review.

## Auditor Access

Auditor packet for one deployment should include:

- OVERT scope statement;
- sample valid `.aep` package;
- sample tampered package or test vector;
- Java verifier version and checksum;
- policy id/version and policy registry export;
- signing key history for the claim period;
- TSA trust anchor material;
- ledger block export for the relevant tenant and time window;
- incident/disclosure log for the claim period;
- exclusions and known limitations.

## Incident Disclosure

Integrity-impacting incidents include:

- signing key compromise or suspected compromise;
- evidence-package generation bug that can produce unverifiable artifacts;
- verifier bug that accepts invalid packages;
- ledger chain corruption;
- unauthorized suppression, modification, or delayed publication of attestation
  artifacts;
- TSA trust-anchor misconfiguration that affects verification.

Target handling:

1. Triage and preserve logs immediately.
2. Freeze affected key or service where needed.
3. Notify affected operators and assessors within 72 hours of detection.
4. Publish corrected verifier/test vectors if the issue affects relying parties.
5. Record remediation in the next transparency report.

## Portability Escrow

The export format should allow a replacement IAP to resume service and allow an
auditor to verify history. Minimum export:

```text
tenant/
  scope-statement.json
  policies/
  keys/
  trust-anchors/
  ledger-blocks.jsonl
  attestations.jsonl
  evidence-packages/
  verifier/
  incidents.jsonl
  manifest.json
```

`manifest.json` should include file hashes, export time, source deployment,
schema versions, and signer identity.

## Immediate Actions

- Add this pack to the external review pack.
- Create a concrete IAP operating policy from this template.
- Create the portability escrow JSON schema.
- Add a monthly transparency metric export job or documented manual query.
- Attach one real MCP attest-mode evidence sample to the assessor packet.
