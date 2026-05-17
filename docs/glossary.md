# Glossary

**Status:** v0.1 (2026-05-17). Stable for the v0.1 line; new terms
added as the spec evolves.

This glossary covers EATF-specific terminology, the standards EATF
relates to, and the standards-relationship label set used across
the documentation.

For positioning rationale see [`design-rationale.md`](design-rationale.md);
for the wire format see [`aep-profile.md`](aep-profile.md).

## EATF-specific terms

**AEP — Agent Evidence Package.** A self-contained, offline-
verifiable ZIP artefact documenting an agent's action. The wire
format is documented in [`aep-profile.md`](aep-profile.md). File
extension: `.aep`. Profile URN: `urn:eatf:spec:aep:1.0` for v0.1.

**Agent attestation.** A signed claim about an agent (identity,
capability, operator mandate, policy decision on a specific
action). Embedded in an AEP via `metadata.json`, the OVERT receipt,
and optionally `attestations/agent.vc.json`. See
[`attestation-profile.md`](attestation-profile.md) for the format
of the latter.

**Agent ID (URN).** Tenant-bound URN of the form
`urn:eatf:tenant:<tenantId>:agent:<slug>`. Carried in
`metadata.agent_id` and `receipt.subject.agent_id`. The
`urn:uuid:<uuid>` legacy form is also accepted by v0.1 verifiers.

**Canonical bytes / `canonical.bin`.** The deterministic byte
sequence that signatures and hashes are computed over. The v0.1
profile defines two forms:
- **AEP profile form:** `response.txt || LF || JCS(metadata.json)`.
- **Java response-only form:** `response.txt` verbatim.
The verifier accepts both for backwards compatibility with the
Java reference implementation.

**Framework Operations Statement (FOS).** Non-TSP description of
how an operator runs the EATF reference implementation. Replaces
the TSPS framework used by qualified trust service providers under
ETSI TS 119 402. Tyche Institute publishes a FOS for the
eatf.eu reference deployment at
[`/legal/framework-operations`](https://eatf.eu/legal/framework-operations).

**Issuer.** The operator entity whose private key signed the
package. Identified by the certificate or public key in
`public_key.pem` (and `pqc_public_key.pem` when present).

**JCS — JSON Canonicalization Scheme.** IETF RFC 8785. The byte-
level canonicalisation EATF uses for all JSON content that gets
signed. See `lib/src/canonical.ts` for the reference implementation.

**ML-DSA-65.** NIST FIPS 204 module-lattice digital signature
algorithm at parameter set 65 (also known historically as
CRYSTALS-Dilithium3). EATF's post-quantum signature suite,
identified by URN `urn:eatf:sig:mldsa-65`.

**OVERT.** Observable Verification Evidence for Runtime Trust. A
small JSON profile that EATF embeds inside each AEP as
`overt_receipt.json`, recording scope, subject, event, policy, the
hash of the signed bytes, and witness file pointers. v0.1 receipts
declare `"overt": "1.0.0"` and `"profile": "urn:eatf:spec:aep:1.0"`.
Schema in `schemas/overt-receipt-v1.schema.json`.

**Private CA.** A certificate authority operated by an EATF
deployment for issuing certificates to its agents. Not a public
trust service. Verifiers trust a deployment's private CA only if
they have been configured with the corresponding root anchor.

**QEAA — Qualified Electronic Attestation of Attributes.** Defined
by eIDAS Article 3(45). Issued by Qualified Trust Service Providers.
**EATF attestations are NOT QEAAs.**

**QTSP — Qualified Trust Service Provider.** Defined by eIDAS
Article 3(20). Granted qualified status by a national supervisory
body and appearing on an EU/EEA Trusted List. **Tyche Institute
is NOT a QTSP.**

**TSA — Time-Stamping Authority.** An RFC 3161 timestamping
server. EATF embeds an RFC 3161 `TimeStampToken` in every AEP at
`timestamp.tsr`, binding the manifest signature to a trusted
wall-clock time. Each deployment selects its own TSA; EATF itself
does not operate as a TSA.

**Trust anchor.** A self-signed certificate or public key that a
verifier has been pre-configured to trust. Verifiers maintain
separate anchor sets for issuer CAs (Layer 3) and for time-stamping
authorities (Layer 4).

**VC — Verifiable Credential.** W3C VC Data Model 2.0. The data
model used for the optional `attestations/agent.vc.json` entry
inside an AEP.

## Standards-relationship labels

The four labels distinguish *technical implementation* from
*regulatory conformance*. Neither label implies the other. Full
context in [`architecture.md`](architecture.md) §"Standards-
relationship legend".

**IMPLEMENTED.** The reference implementation in `lib/` realises
the standard end-to-end and is covered by test vectors in
`test-vectors/`. Example: RFC 8785 JCS.

**ALIGNED.** The reference implementation follows the standard's
required structures and semantics but has not been independently
conformance-tested. Example: RFC 3161 timestamps.

**REFERENCED.** The standard is cited for design vocabulary or
policy reasoning; this project does not claim to implement it.
Examples: ETSI EN 319 401 (applies to TSPs; EATF is not a TSP),
RFC 3647 (CP/CPS framework).

**ADDRESSED.** A regulatory or policy reference; the project
documents how the regulation bears on EATF's positioning but does
not itself fulfil the regulation. Examples: EU AI Act Articles 12,
14, 50; eIDAS Article 3(16).

## Implementation-maturity labels

These appear on the public-site architecture diagram next to each
component pill. They are orthogonal to the standards-relationship
labels above and describe the state of a given module in the
reference implementation.

- **PRODUCTION** — operational in reference deployments. Does NOT
  indicate external certification, third-party audit, or
  regulatory approval.
- **WORKING** — functional but not yet production-mature.
- **PARTIAL** — partially implemented.
- **PROTOTYPE** — early-stage implementation.
- **STUB** — placeholder; no real behaviour yet.
- **PLANNED** — not yet implemented or certified.

## Cryptographic primitives

**ECDSA-P256.** ECDSA over the NIST P-256 curve with SHA-256
digest. Identified by URN `urn:eatf:sig:ecdsa-p256`. Alternative
to RSA-PSS at Layer 3.

**Hybrid signing.** The practice of carrying two signatures over
the same bytes — one classical (RSA or ECDSA) and one post-
quantum (ML-DSA-65). Verifiers MUST validate both when both are
present. Bounds the damage if either suite is later cryptanalysed.

**PKCS#1 v1.5 / RSASSA-PKCS1-v1_5.** Legacy RSA signature padding
defined in RFC 8017. EATF's v0.1 reference packages use this
padding (matches the Java reference implementation). The verifier
also supports RSA-PSS but the bundled signer does not emit it.

**RFC 3161.** IETF Time-Stamp Protocol over PKI. Format used for
the `timestamp.tsr` entry. The verifier accepts the standard ASN.1
encoding either raw or base64-wrapped.

**RSA-4096.** RSA at 4096-bit modulus, the default classical
signature suite. Identified by URN `urn:eatf:sig:rsa4096`.

**SHA-256.** NIST FIPS 180-4. The hash function for all v0.1
operations.

## Regulatory references

**EU AI Act / Regulation (EU) 2024/1689.** The EU regulation
governing AI systems with risk-based obligations. EATF's design
is informed by Article 12 (record-keeping), Article 14 (human
oversight), Article 50 (transparency obligations), and Annex IV
(technical documentation). EATF does NOT certify AI Act
compliance — that posture remains the deploying operator's
responsibility.

**eIDAS / Regulation (EU) 910/2014, as amended by
Regulation (EU) 2024/1183 ("eIDAS 2.0").** The EU regulation
governing electronic trust services. **EATF is not a trust
service under Article 3(16)** of this regulation. EATF agent
attestations **do not constitute QEAA under Article 3(45)**. The
positioning is load-bearing for the project's legal posture and
appears verbatim in `NOTICE`, README, and the Framework Operations
Statement.

**GDPR / Regulation (EU) 2016/679.** Data-protection regulation.
EATF's selective-disclosure (SD-JWT) feature is useful for
operators implementing GDPR Article 5(1)(c) data-minimisation
patterns. EATF does not certify GDPR compliance — that posture
remains the deploying controller's responsibility.

## Process terms

**Conformance.** An implementation claims v0.1 conformance if it
reports the contract-specified `verify=true | false` outcome for
every package in `test-vectors/`. Diagnostic text MAY differ.

**Round-trip.** Producing an `.aep` with `eatf-sign` and verifying
the same file with `eatf-verify`. The repository includes one
round-trip test vector
(`test-vectors/valid/minimal-roundtrip/`) and a CI job that
performs the round-trip on every push.

**Tamper class.** A category of post-sign modification that the
verifier must detect. v0.1 names six tamper classes via the
`test-vectors/invalid/` set; see [`threat-model.md`](threat-model.md)
for the full STRIDE mapping.

## Related documents

- [`aep-profile.md`](aep-profile.md) — wire-format specification.
- [`architecture.md`](architecture.md) — layered structure.
- [`threat-model.md`](threat-model.md) — STRIDE analysis.
- [`attestation-profile.md`](attestation-profile.md) — W3C VC
  profile for the optional attestation entry.
- [`design-rationale.md`](design-rationale.md) — why each design
  choice.
