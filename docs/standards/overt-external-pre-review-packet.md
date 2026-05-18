---
title: "OVERT External Pre-Review Packet"
description: "Reviewer-facing packet, request template, and expected checks for EATF OVERT pre-review."
audience: ["developers", "partners"]
tags: ["overt", "review", "assessor", "submission"]
last_updated: "2026-05-14"
---

# OVERT External Pre-Review Packet

Status: ready-to-send draft. This packet supports external review only; it is
not a public conformance claim.

## TLDR

Send this packet only to a named reviewer, assessor candidate, or pilot
customer auditor. Do not publish it as proof of conformance.

Ask the reviewer to answer one question:

```text
Is the proposed EATF AEP + MCP tools/call scope reviewable as an OVERT 1.0
Level 2 Agentic-Extended readiness claim, and what must change before any
public claim or profile-registry submission?
```

## Attachment List

| Purpose | Artifact |
|---|---|
| Scope and claim boundary | `docs/standards/overt-1.0-conformance-readiness.md` |
| Control mapping | `docs/standards/overt-level2-agentic-control-mapping.md` |
| AEP protocol profile | `docs/specs/aep-profile-v1.md` |
| MCP agentic profile | `docs/specs/mcp-attestation-profile-v1.md` |
| Submission summary | `docs/standards/overt-profile-submission-pack.md` |
| IAP operating posture | `docs/standards/overt-iap-operating-pack.md` |
| External review cover sheet | `docs/partners/external-review-pack.md` |
| Golden fixtures | `backend/src/test/resources/fixtures/overt/` |
| Java verifier | `backend/src/main/java/ai/aletheia/verifier/EvidenceVerifierImpl.java` |
| TypeScript verifier | `sdks/eatf-verifier-ts/src/verifier.ts` |

## Reviewer Checks

Ask the reviewer to check:

1. The claim boundary excludes non-MCP paths, Level 3 statistical claims, and
   Level 4 preservation claims.
2. `overt_receipt.json` is sufficient as an additive OVERT profile receipt
   inside `.aep`.
3. The Java verifier rejects the tampered fixture and accepts the valid/MCP
   fixtures.
4. The MCP fixture actually represents `tools/call` scope and not generic
   sign-mode evidence.
5. IAP independence, operating-policy, and portability gaps are clearly
   disclosed.
6. The profile is ready for informal review, or the reviewer identifies
   blockers before formal submission.

## Expected Verifier Commands

Run from repository root:

```bash
cd backend
./mvnw -Dtest=OvertFixtureVerificationTest test
```

Expected result:

```text
valid-overt-profile.aep                  -> valid
tampered-overt-receipt.aep               -> invalid, overt receipt invalid
mcp-tools-call-valid.aep                 -> valid, scope agentic-extended:mcp-tools-call
mcp-tools-call-denied-policy.aep         -> valid package, policy.decision deny
```

For the TypeScript verifier:

```bash
cd sdks/eatf-verifier-ts
npm test -- overt-fixtures.test.ts
```

## Email Template

```text
Subject: Request for OVERT pre-review: EATF AEP + MCP tools/call profile

Hello <reviewer>,

We are preparing a narrow OVERT 1.0 readiness review for EATF's evidence
package and MCP tools/call attestation path. We are not asking you to certify
or endorse the system. We are asking for a pre-review of whether the attached
scope, profile, receipt schema, verifier, and fixtures are reviewable as a
future OVERT Level 2 Agentic-Extended claim.

Proposed scope:
OVERT 1.0 Level 2 Agentic-Extended readiness for MCP tools/call attestation
through @eatf/mcp-gateway and EATF .aep evidence packages.

Specific asks:
1. Identify claim-language or scope overreach.
2. Review the AEP + OVERT receipt schema.
3. Run or inspect the Java verifier against the valid/tampered/MCP fixtures.
4. Identify gaps before any public claim or formal profile-registry submission.

We will track every finding in docs/standards/overt-review-feedback-register.md.

Thank you,
EATF maintainer team
```

## Send Rules

- Send only after the recipient is known and approved internally.
- Do not include secrets, production keys, customer data, or production logs.
- Use the fixture keys only.
- Do not ask for "certification" at pre-review stage.
- Do not state or imply that OVERT has approved EATF.
