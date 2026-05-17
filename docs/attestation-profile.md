# Agent attestation profile

**Status:** v0.1 (2026-05-17). The current v0.1 packages do NOT
yet embed a separate `attestations/agent.vc.json` entry — agent
identity and policy decisions are carried inside `metadata.json`
and the OVERT receipt instead. This document specifies the W3C VC
profile EATF will use *when* an embedded VC entry is added in a
later 0.1.x point release. Operators producing packages today
should follow the metadata.json + OVERT-receipt path documented
in [`aep-profile.md`](aep-profile.md) §5.

This document is therefore both a **specification** (for the
forward-compatible VC entry) and a **non-implementation marker**
(the entry is not in v0.1 packages yet).

## Positioning

EATF agent attestations are technical self-attestations of agent
identity, capability claims, and operator-asserted bindings. They
are **NOT** Qualified Electronic Attestations of Attributes
(QEAA) under eIDAS Article 3(45) and have **no eIDAS legal
effect**. They are not issued by a Qualified Trust Service
Provider; the signing CA in v0.1 deployments is a private CA
operated by the deployment.

A relying party that needs a qualified attestation under eIDAS
should obtain it from a QTSP — not from EATF.

## VC profile (when embedded)

The attestation, when present, lives at the package path
`attestations/agent.vc.json` and is a W3C Verifiable Credential
2.0 document with the following profile constraints.

### Required structure

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://schemas.tyche.institute/eatf/context-v1.jsonld"
  ],
  "type": ["VerifiableCredential", "EATFAgentAttestation"],
  "issuer": {
    "id": "did:web:<deployment-host>",
    "name": "<deployment human name>"
  },
  "validFrom": "2026-05-17T00:00:00Z",
  "validUntil": "2027-05-17T00:00:00Z",
  "credentialSubject": {
    "id": "urn:eatf:tenant:<tenant>:agent:<slug>",
    "agentType": "custom",
    "riskClassification": "high",
    "capabilities": ["regulatory-qa", "human-in-the-loop"],
    "policyId": "atap-basic",
    "policyVersion": "1.0"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "verificationMethod": "did:web:<host>#issuer-key-2026-05",
    "proofPurpose": "assertionMethod",
    "created": "2026-05-17T00:00:00Z",
    "proofValue": "z..."
  }
}
```

### Field constraints

| Field                          | Required | Constraint                                                              |
|--------------------------------|----------|-------------------------------------------------------------------------|
| `@context`                     | yes      | MUST include the W3C VC 2.0 context. MAY include the EATF v1 context.   |
| `type`                         | yes      | MUST include `"VerifiableCredential"` and `"EATFAgentAttestation"`.     |
| `issuer.id`                    | yes      | DID identifier for the issuing deployment.                              |
| `issuer.name`                  | recommended | Human-readable name of the deployment.                               |
| `validFrom`                    | yes      | ISO 8601 timestamp.                                                     |
| `validUntil`                   | recommended | ISO 8601 timestamp. When absent, verifier MUST treat as time-unbounded but SHOULD warn. |
| `credentialSubject.id`         | yes      | EATF agent URN. MUST equal `metadata.agent_id` in the enclosing AEP.    |
| `credentialSubject.agentType`  | yes      | Free-form string. MUST match `metadata.agent_type` when both present.   |
| `credentialSubject.riskClassification` | yes | One of `minimal`, `limited`, `high`. Refers to EU AI Act risk tiers. |
| `credentialSubject.capabilities` | recommended | Free-form list of strings describing what the agent is allowed to do.|
| `credentialSubject.policyId`   | recommended | MUST match `metadata.policy_id` when both present.                   |
| `credentialSubject.policyVersion` | recommended | MUST match `metadata.policy_version` when both present.            |
| `proof`                        | yes      | W3C DataIntegrityProof. Signing key MUST resolve to a public key the verifier can validate against the deployment's configured trust anchors. |

### Cross-document consistency

When both `metadata.json` and `attestations/agent.vc.json` are
present, the following fields MUST be byte-equal:

- `metadata.agent_id` ↔ `credentialSubject.id`
- `metadata.policy_id` ↔ `credentialSubject.policyId` (if both present)
- `metadata.policy_version` ↔ `credentialSubject.policyVersion` (if both present)

A verifier MUST reject the package on any cross-document
inconsistency. The v0.1 verifier in
[`lib/src/verifier.ts`](../lib/src/verifier.ts) will surface this
check once the embedded-VC path lands.

## Signing modes

Two modes are anticipated for the embedded-VC release:

### 1. Private-CA mode (default)

The VC's `proof.verificationMethod` references a key whose
certificate chains to a private root operated by the deployment.
Verifiers trust the chain only when configured with the
corresponding root anchor.

This is the same model EATF uses for `public_key.pem` over
`canonical.bin` at the package level. No new trust assumption is
introduced.

### 2. External-issuer-bound mode

The VC carries an additional `evidence` block referencing a
credential issued externally (e.g. by a QTSP). EATF does not
itself issue the external credential; the embedded VC carries
the reference and the verifier validates the external credential
against the external issuer's published trust list, separate from
EATF's trust list.

The embedded VC's own `proof` MUST still be valid (private-CA
signed). The external reference is additive, not substitutive.

## What this profile does NOT prescribe

- **Mandate vocabulary.** The `capabilities` and policy fields are
  free-form in v0.1. A future revision MAY introduce a controlled
  vocabulary (URN-based) once enough deployments exist to identify
  the recurring terms.
- **Revocation surface.** v0.1 has no mechanism for revoking an
  embedded VC. Operators rotating keys MUST publish key rotation
  events in their public-key history mirror.
- **Multi-signature VCs.** Each VC carries exactly one `proof`. Joint
  attestations (multiple signers on one VC) are out of scope for
  v0.1.
- **Selective disclosure / SD-JWT on the VC itself.** The VC
  carried inside an AEP is the full credential. SD-JWT for
  user-facing selective disclosure is an operator-side concern
  (see `frontend/app/disclosures/page.tsx` for the reference
  deployment's UX); it is not part of the VC profile here.

## Verifier behaviour (when the entry is present)

```
1. Parse attestations/agent.vc.json as W3C VC 2.0.
2. Validate the structure against this profile.
3. Cross-check fields against metadata.json (see above).
4. Verify proof.proofValue against proof.verificationMethod.
5. Resolve the verification key to a configured trust anchor
   (deployment-specific issuer trust list).
6. Reject the package on any step's failure.
```

The current v0.1 verifier code skips steps 1-6 because the entry
is not in any production package. The cross-check infrastructure
is already in place via [`lib/src/overt.ts`](../lib/src/overt.ts);
the embedded-VC path will reuse the same cross-check helpers.

## Related documents

- [`aep-profile.md`](aep-profile.md) §5 — current `metadata.json`
  shape, which carries the same logical content as the future
  embedded VC.
- [`architecture.md`](architecture.md) — Layer 5 (envelope) and
  Layer 6 (orchestration), where this entry would be parsed and
  cross-checked.
- [`glossary.md`](glossary.md) — definitions of QEAA, QTSP, VC,
  DID, and the EATF agent URN format.
- [`threat-model.md`](threat-model.md) §"E1" — the capability-
  inflation threat this entry mitigates.

## Coming next

The embedded VC entry lands in a 0.1.x point release once two
preconditions are met: (1) at least two independent operators are
ready to consume it, and (2) the SLH-DSA / hybrid proof-suite
question for VC `proof` is settled upstream (the W3C VC working
group's PQC proof suite is in active draft). Until then,
operators carry agent identity in `metadata.json` and the OVERT
receipt as documented above.
