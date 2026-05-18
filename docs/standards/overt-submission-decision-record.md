---
title: "OVERT Submission Decision Record"
description: "Decision path for external pre-review, OVERT profile submission, and public claim timing."
audience: ["developers", "partners"]
tags: ["overt", "decision", "submission", "conformance"]
last_updated: "2026-05-14"
---

# OVERT Submission Decision Record

Status: decision prepared; formal external submission not yet sent.

## TLDR

Do not submit directly to the OVERT registry yet. Run an external pre-review
first using the narrow MCP tools/call scope. Formal submission becomes
reasonable only after reviewer findings are closed.

## Decision

Recommended path:

1. Use the current repository artifacts as the internal bundle.
2. Send the external pre-review packet to one named independent reviewer or
   pilot customer auditor.
3. Fix findings in `overt-review-feedback-register.md`.
4. If findings are clean, submit the protocol profile to the OVERT registry
   maintainer or publish a self-declared Level 1/2 profile according to the
   chosen route.
5. Keep public copy on "OVERT-aligned; conformance work in progress" until
   the review path is complete.

## Options Considered

| Option | Decision | Reason |
|---|---|---|
| Keep internal only | Not enough | Good for readiness, but does not test external credibility. |
| External pre-review first | Recommended | Lowest-risk way to catch overclaiming and profile gaps. |
| Submit protocol profile now | Defer | Registry-facing submission should follow external technical review. |
| Public conformance claim now | Reject | Not supported; no external review, IAP evidence, or registered profile. |

## Submission Target

When ready, route to the OVERT review / protocol profile channel identified by
the OVERT maintainer. Current public contact is:

```text
overt-review@glacis.io
```

Before sending, verify the latest OVERT version feed:

```text
https://overt.is/latest.json
```

## Minimum Gate For Formal Submission

- External pre-review completed.
- No open blocker findings.
- Major findings closed or explicitly excluded.
- Java and TypeScript fixture tests passing.
- OVERT receipt schema and AEP profile frozen for the submission tag.
- IAP operating pack complete enough to answer independence, incident,
  portability, uptime, and key-management questions.

## Current Decision State

```text
state: pre-review-ready
formal_submission: not_sent
public_claim: OVERT-aligned; conformance work in progress
first_scope: MCP tools/call attestation through @eatf/mcp-gateway and .aep
next_human_action: select external reviewer or pilot auditor
```
