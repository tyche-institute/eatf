---
title: "OVERT Review Feedback Register"
description: "Tracking register for OVERT pre-review and assessor feedback."
audience: ["developers", "partners"]
tags: ["overt", "review", "feedback", "assessor"]
last_updated: "2026-05-14"
---

# OVERT Review Feedback Register

Status: empty until an external reviewer is selected. Use this register to
avoid losing assessor feedback or silently changing claim language.

## Intake Rule

Every external comment gets a row. No public OVERT claim may be made while a
blocking or major finding remains open.

## Severity

| Severity | Meaning | Required action |
|---|---|---|
| Blocker | Public claim or profile submission would be misleading or technically unsupported. | Fix before any external statement or submission. |
| Major | The claim may be reviewable, but a material evidence or operating gap remains. | Fix or explicitly exclude before submission. |
| Minor | Clarification, editorial issue, or non-blocking evidence improvement. | Fix before final publication where practical. |
| Question | Reviewer needs more context. | Answer in writing and convert to a finding if needed. |

## Register

| ID | Date | Reviewer | Severity | Topic | Finding | Owner | Status | Resolution |
|---|---|---|---|---|---|---|---|---|
| OVR-001 | 2026-05-14 | internal dry run | Major | Scope | First claim must remain limited to MCP tools/call; non-MCP platform claims are not supported. | maintainer | closed | Scope docs and claim language constrain first claim to MCP tools/call. |
| OVR-002 | 2026-05-14 | internal dry run | Major | Fixtures | External reviewers need an MCP-specific fixture, not only a generic AEP fixture. | maintainer | closed | Added `mcp-tools-call-valid.aep` and `mcp-tools-call-denied-policy.aep`. |
| OVR-003 | 2026-05-14 | internal dry run | Minor | Policy decision | Denied-policy fixtures should show denial as a policy outcome while remaining cryptographically valid. | maintainer | closed | Added `policy.decision` to OVERT receipt and metadata-bound verifier checks. |
| OVR-004 | 2026-05-14 | internal dry run | Question | External reviewer | No actual third-party reviewer has received the packet yet. | maintainer | open | Select reviewer or pilot auditor before marking external pre-review complete. |

## Closure Checklist

Before changing status to ready for formal submission:

- all blocker findings closed;
- all major findings either closed or explicitly excluded from scope;
- reviewer has confirmed final claim language in writing;
- fixtures and verifier commands pass in CI;
- profile submission pack points to the exact reviewed commit or release tag.
