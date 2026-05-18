# Kratt Manifest — open spec

> **Status:** draft v0.1, 2026-04. This is an *open spec*, not a regulation.
> Estonian public-sector AI agents ("Kratts") are coordinated by RIA /
> Government CIO Office under the [AI and Data Action Plan
> 2024–2026](https://regulations.ai/regulations/estonia-2024-03-kratt-action-plan-2024-2026).
> [kratid.ee](https://kratid.ee/en) is the public information hub. This
> spec describes how a Kratt can opt into the **Aletheia Accountability
> Kit** so its runtime activity is signed, auditable, and verifiable.

## Why this spec exists

[Bürokratt 2026](https://www.ria.ee/en/state-information-system/personal-services/burokratt)
shifts from one central chatbot to "a unified network of agents" — each
Estonian public-sector institution will run its own personalised AI
agent. None of those agents come with built-in accountability primitives:
signed responses, hash-chained audit, citizen-facing evidence. This spec
defines the minimum manifest fields that turn any Kratt into a
governance-ready agent that:

1. publishes its identity at `/.well-known/eatf-agent.json`,
2. signs every response (RSA-4096 + ML-DSA-65),
3. timestamps every signature via RFC 3161,
4. holds high-risk decisions for human review,
5. emits an offline-verifiable `.aep` evidence package per session.

## Manifest fields

A Kratt manifest is an EATF agent `agent.yaml` with the **Kratt
extension** fields below. The extension is **all-or-nothing**: if any
`kratt_*` / `well_known_url` / `tsa_url` / `evidence_retention_years`
field is set, the full set is required. Agents that don't position
themselves as Kratts (e.g. legal-firm agents in OpenCourt) just omit
all extension fields and the schema lets them through.

Required fields when adopting the Kratt extension are marked •.

```yaml
# Identity
agentId:                  urn:uuid:<uuid>            # • stable across redeploys
displayName:              "TTA-Konsultant"           # •
description:              "Public consultant on unemployment benefits"

# Kratt-extension fields (this spec)
kratt_id:                 KRA-2026-0142              # • see § Conventions
kratt_owner:              "Eesti Töötukassa"         # • legal entity
kratt_purpose:            "First-line citizen support on benefit eligibility"   # •
risk_class:               HIGH                       # • LOW | MEDIUM | HIGH
human_review_required:    true                       # • for risk_class >= MEDIUM
tsa_url:                  "https://tsa.skidsolutions.eu/RFC3161"  # • RFC 3161 endpoint
evidence_retention_years: 10                         # • minimum citizen-facing retention
well_known_url:           "https://tta.ee/.well-known/eatf-agent.json"   # •
kratid_listing_url:       "https://kratid.ee/en/tta-konsultant"   # optional, for visibility

# Inherited from base EATF agent manifest
agentType:                custom
eidasLevel:               qualified
signatureAlgorithm:       HYBRID
primaryJurisdiction:      EE

capabilities:
  - regulatory-qa
  - human-in-the-loop
  - evidence-package
```

## Conventions

### `kratt_id`

A short stable handle for the Kratt across documents, signage, and
evidence-package metadata. Recommended format `KRA-<YYYY>-<sequence>` for
public-sector Kratts; private-sector Kratts use whatever convention they
prefer. Aletheia does not validate this against any external registry.

### `risk_class`

Triggers behaviour:

| Value | Required runtime behaviour |
|---|---|
| LOW | Sign + timestamp every response. No human-review gate. |
| MEDIUM | All of LOW + human review may be invoked by policy or risk score. |
| HIGH | All of MEDIUM + human review is mandatory before release for any prompt that triggers a `policy_hit`. |

Mirrors the AI Act risk classification spirit; not a legal classification.

### `well_known_url`

Each Kratt MUST serve a public manifest at `/.well-known/eatf-agent.json`
on its own domain. The endpoint is unauthenticated and contains:

```json
{
  "kratt_id": "KRA-2026-0142",
  "agentId": "urn:uuid:...",
  "owner": "Eesti Töötukassa",
  "purpose": "...",
  "risk_class": "HIGH",
  "governance": {
    "framework": "Aletheia EATF",
    "version": "0.1",
    "evidence_endpoint": "https://api.eatf.eu/api/v1/evidence/by-kratt/KRA-2026-0142",
    "verify_url": "https://eatf.eu/scenarios/kratid/verify/<chain-or-evidence-id>",
    "public_keys": [
      { "alg": "RSA-4096", "kid": "...", "pem": "..." },
      { "alg": "ML-DSA-65", "kid": "...", "der_b64": "..." }
    ]
  },
  "stats_24h": {
    "signed_responses": 1284,
    "human_reviews": 7,
    "last_evidence_at": "2026-04-30T09:21:14Z"
  }
}
```

The manifest is the trust anchor: a verifier (citizen, journalist,
auditor) reads it directly from the Kratt's domain, then verifies any
`.aep` bundle the Kratt produced, with no Aletheia round-trip required.

### `evidence_retention_years`

Citizen-facing retention floor. Education (18+), healthcare (10+),
legal (10+) are the high-end cases — pin the value to the longest
plausible window, because that drives whether ML-DSA hybrid signing is
*nice-to-have* or *load-bearing*.

## Embed badge

Once a Kratt has a `well_known_url`, the institution can embed a live
trust badge anywhere — its own site, an information page on
[kratid.ee](https://kratid.ee/en), or a sub-page of a partner agency:

```html
<script src="https://eatf.eu/badge.js"
        data-kratt="KRA-2026-0142"
        async></script>
```

The badge fetches the well-known manifest and renders activity stats
(signed responses last 7 days, last evidence timestamp, last verification
result). Aletheia does not pull from the institution's site; the
institution chooses what to expose.

## JSON Schema

Machine-readable schema in
[`docs/specs/kratt-manifest.schema.json`](./kratt-manifest.schema.json).

## What this spec is **not**

- Not a legal classification under the EU AI Act. `risk_class` mirrors
  the spirit of Art 6/Annex III but is not authoritative.
- Not a kratid.ee registration. Kratid.ee remains a content site
  curated by Estonian public-sector editors. This spec provides the
  *runtime* substrate; visibility on kratid.ee is a separate editorial
  step.
- Not a profile of EU AI Act technical standards. Where ETSI EN 319
  series or eIDAS profiles overlap, those documents prevail.

## How to adopt — for an Estonian public-sector team

1. Read this spec and `docs/partners/ria-pilot.md`.
2. Provision an EATF tenant (self-hosted or via an Aletheia partner
   instance during pilot phase).
3. Mint an API key, sync `agent.yaml` with `eatf agents sync`.
4. Wire your Kratt's response handler to call `POST /api/sign` for
   every model output, and `POST /api/v1/actions/request` whenever the
   prompt triggers a policy hit.
5. Serve `/.well-known/eatf-agent.json` from your domain.
6. Embed the badge wherever the Kratt has a public surface.

End-to-end demo: `partner-integrations/burokratt-kit/`.
