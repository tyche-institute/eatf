---
title: "OVERT Profile Submission Pack"
description: "Draft material for submitting the EATF AEP and MCP attestation profiles for OVERT-oriented review."
audience: ["developers", "partners"]
tags: ["overt", "standards", "profile", "attestation"]
last_updated: "2026-05-14"
---

# OVERT Profile Submission Pack

Status: draft preparation material. This is not an OVERT conformance claim.

## TLDR

Use `.aep` as the package. Do not introduce a second OVERT-only extension.
OVERT alignment is represented by the additive `overt_receipt.json` entry,
the Java verifier checks, and the golden valid/tampered vectors.

Candidate submission name:

```text
EATF AEP Profile v1 with OVERT 1.0 receipt
```

Candidate first assessment scope:

```text
OVERT 1.0 Level 2 Agentic-Extended readiness for MCP tools/call
attestation through @eatf/mcp-gateway and EATF .aep evidence packages.
```

## Submission Bundle

Attach these materials together:

| Item | Repository artifact |
|---|---|
| Protocol profile | `docs/specs/aep-profile-v1.md` |
| Agentic profile | `docs/specs/mcp-attestation-profile-v1.md` |
| OVERT receipt schema | `docs/specs/aep-profile-v1.md`, section 4.1 |
| Operating posture | `docs/standards/overt-iap-operating-pack.md` |
| Readiness matrix | `docs/standards/overt-1.0-conformance-readiness.md` |
| Control mapping | `docs/standards/overt-level2-agentic-control-mapping.md` |
| External pre-review packet | `docs/standards/overt-external-pre-review-packet.md` |
| Feedback register | `docs/standards/overt-review-feedback-register.md` |
| Submission decision record | `docs/standards/overt-submission-decision-record.md` |
| External-review cover sheet | `docs/partners/external-review-pack.md` |
| Java verifier | `backend/src/main/java/ai/aletheia/verifier/EvidenceVerifierImpl.java` |
| TypeScript verifier | `sdks/eatf-verifier-ts/src/verifier.ts` |
| Golden OVERT vectors | `backend/src/test/resources/fixtures/overt/` |

## Profile Summary

The EATF AEP Profile v1 defines a flat ZIP package with deterministic
canonical bytes, SHA-256 binding, RSA signature, optional ML-DSA signature,
RFC 3161 timestamping, metadata, and an optional OVERT receipt. The OVERT
receipt binds:

- OVERT version and AEP profile identifier;
- assessment scope;
- subject identity and tenant hash where available;
- event type, timestamp, and action type;
- policy version and coverage where available;
- `sha256:` content hash copied from `hash.sha256`;
- witness file references inside the same `.aep`.

The receipt is intentionally inside the evidence package so existing package
distribution, storage, and verifier UX remain unchanged.

## Evidence Samples

Required vectors before external review:

| Vector | Expected verifier result |
|---|---|
| `valid-overt-profile.aep` | Valid; reports `overt_receipt: OK`. |
| `tampered-overt-receipt.aep` | Invalid; reports `overt receipt invalid`. |
| `mcp-tools-call-valid.aep` | Valid; scope `agentic-extended:mcp-tools-call`; `policy.decision=allow`. |
| `mcp-tools-call-denied-policy.aep` | Valid package containing `policy.decision=deny`, not a successful action claim. |

## Open Items

- Select a named external reviewer or pilot auditor.
- Close open findings in `docs/standards/overt-review-feedback-register.md`.
- Decide whether the first public posture should be Level 1 or Level 2 after
  reviewer feedback.
- Keep public copy on "OVERT-aligned; conformance work in progress" until the
  assessment path is complete.

## Version Tracking

OVERT latest version feed checked on 2026-05-14:

```text
https://overt.is/latest.json -> 1.0.0
```
