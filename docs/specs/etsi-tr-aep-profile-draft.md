<!-- markdownlint-disable MD013 MD028 MD034 MD036 MD041 -->

# ETSI TR (draft) — Aletheia Evidence Package (AEP): a non-qualified evidence profile for AI agent action attestation

**Document identifier (working):** `urn:eatf:etsi-tr-aep:0.1`
**Version:** 0.1-draft, dated 2026-05-12.
**Status:** working draft for ETSI workstream submission. Not an ETSI deliverable. Comment period open through 2026-08-12.
**Maintainer:** EATF.eu (`security@aletheia.ai`).
**Companion documents:** `docs/specs/aep-profile-v1.md` (normative), `docs/legal/TSPS.md` (informative), `docs/legal/etsi-en-319-401-self-assessment.md` (informative).

---

## Foreword

> *Placeholder. In a published ETSI Technical Report this paragraph is composed by the relevant Technical Committee (here, presumed ESI WG3/WG4) and identifies the workstream, rapporteur and superseded publications. EATF supplies an interim text to be replaced on adoption.*

The present document has been produced as a contribution to the ESI workstream on signature and trust formats specialised for autonomous and semi-autonomous AI agents. It is offered for review by the relevant Working Group and is **not** an approved ETSI deliverable. The contributing organisation is EATF (Enterprise Agent Trust Framework), codename Aletheia AI — a non-qualified trust-service operator based in the European Union — which operates a signing service for AI agent actions and emits the `.aep` evidence package described herein.

The contribution rests on three premises. First, Regulation (EU) 2024/1689 (AI Act) and Directive (EU) 2022/2555 (NIS2) create record-keeping, transparency and traceability obligations that existing ETSI signature formats do not directly address. Second, the cryptographic primitives required to discharge those obligations are already standardised (RFC 3161, 5280, 8017, FIPS 180-4, FIPS 204) and need only assembly into a profile. Third, the assembled profile should be **non-qualified** in v1 so that a working draft can be exercised at scale before any qualification claim is contemplated. The submission targets the next ESI plenary and seeks Working Group feedback on the open issues in clause 10. A liaison with CEN-CENELEC JTC 21 is planned for Phase 2.12 and outlined in Annex C.

---

## 1. Introduction

The deployment of artificial-intelligence agents — software entities that produce textual, structural or operational outputs on behalf of a human or organisational principal — has reached a scale at which downstream relying parties (regulators, auditors, insurers, contractual counterparties) require **cryptographic evidence** that a particular output was produced by a particular agent under a particular policy at a particular time. Articles 12, 13, 14, 50 and 72 of the AI Act create record-keeping, transparency, human-oversight and post-market-monitoring duties on providers and deployers of high-risk and general-purpose AI systems; the AI Office and national supervisory bodies are expected to test those duties with concrete documentary requirements during 2026–2027. NIS2 Article 21 adds a cybersecurity baseline overlapping with ETSI EN 319 401.

The technical problem this document addresses is the absence of a profile that:

- Produces a self-contained, offline-verifiable evidence package binding payload bytes, agent identity, model identifier, policy identifier, policy version and a trustworthy time.
- Uses only open, standardised cryptographic primitives so the format outlives any single implementer.
- Is **PQC-ready** today via a hybrid classical + post-quantum signature regime that lets a relying party verify against either signature and that survives deprecation of either primitive.
- Carries no qualification claim under eIDAS but inherits enough of the qualified-TSP operational baseline (EN 319 401, TS 119 402, TS 119 461) to be uplift-compatible if qualification is later pursued.
- Refines, rather than competes with, existing ETSI signature formats — EN 319 122-1 (CAdES), 132-1 (XAdES) and 162-1 (ASiC) — by reusing their building blocks and adding only AI-attestation-specific entries.

The Aletheia Evidence Package (AEP) profile, version 1, defined normatively in `docs/specs/aep-profile-v1.md` and summarised in clause 5, addresses these gaps as a **non-qualified trust-service component**. The package is a ZIP archive carrying canonicalised payload bytes, a hybrid RSA-4096 + ML-DSA-65 signature pair, an RFC 3161 timestamp and a structured metadata document. A reference verifier in Java is open-source; a portable WebAssembly build is scheduled for Phase 1.20.

---

## 2. Scope

The present document specifies a profile, identified `urn:eatf:spec:aep:1.0`, for a self-contained file-based evidence package (file extension `.aep`) emitted by a non-qualified trust service in support of AI agent action attestation under the European Union AI Act and adjacent regulations.

**The document specifies:**

- The container format (a flat ZIP archive without nested directories) and its size envelope.
- The mandatory and optional file entries within the archive, including a structured metadata document (`metadata.json`).
- The deterministic canonicalisation algorithm `eatf-canonical-1`, layered over RFC 8785 (JSON Canonicalisation Scheme).
- The cryptographic primitive catalogue: SHA-256 hashing (FIPS 180-4), RSA-4096 PKCS#1 v1.5 signing (RFC 8017), ML-DSA-65 signing (FIPS 204), and RFC 3161 timestamping.
- The hybrid classical + post-quantum signature regime, including verifier obligations under PQC-enabled and pre-PQC packages.
- The profile-of-profile relationship to ETSI EN 319 122-1 / 132-1 / 162-1.
- The dispute-registry revocation model (in lieu of a classical CRL).
- The conformance taxonomy (strict / transitional / non-conformant) and the location of normative test vectors.
- Security and privacy considerations specific to the AI-attestation use case.

**The document does NOT specify:**

- A qualified trust service under eIDAS Articles 28, 35, 38 or 42. The AEP profile is explicitly non-qualified in v1.
- The internal architecture, scaling regime, or commercial terms of any particular TSP implementing the profile.
- The format of the AI model output itself, beyond the requirement that it be representable as a UTF-8 text payload accompanied by a structured metadata document.
- The semantics of the policy engine evaluated in `attest` mode. Policy semantics are out of scope; the profile records only the policy identifier, version and per-rule coverage report by reference.
- The internal certificate hierarchy of any TSA used for RFC 3161 timestamping.
- Replacement or supersession of any existing ETSI signature format. AEP is a **profile** that reuses ETSI building blocks; it does not deprecate any of them.

The present document is informative in the ETSI sense: it documents a working profile produced by EATF and offered for ESI consideration. Adoption as a normative deliverable is a matter for the relevant Working Group.

---

## 3. References

References are split into normative and informative blocks. Normative references are documents indispensable for the application of the present document. Informative references are those that further explain context or provide supporting material.

### 3.1 Normative references

| Identifier | Title |
| --- | --- |
| IETF RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels. |
| IETF RFC 3161 | Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP). |
| IETF RFC 3339 | Date and Time on the Internet: Timestamps. |
| IETF RFC 5280 | Internet X.509 Public Key Infrastructure Certificate and CRL Profile. |
| IETF RFC 8017 | PKCS #1 v2.2: RSA Cryptography Specifications. |
| IETF RFC 8785 | JSON Canonicalisation Scheme (JCS). |
| IETF RFC 8949 | Concise Binary Object Representation (CBOR). |
| FIPS PUB 180-4 | Secure Hash Standard (SHS), including SHA-256. |
| FIPS PUB 204 | Module-Lattice-Based Digital Signature Standard (ML-DSA). |
| ETSI EN 319 122-1 | CAdES — CMS Advanced Electronic Signatures — Building blocks. |
| ETSI EN 319 132-1 | XAdES — XML Advanced Electronic Signatures — Building blocks. |
| ETSI EN 319 162-1 | Associated Signature Containers (ASiC) — Building blocks. |
| ETSI EN 319 401 | General Policy Requirements for Trust Service Providers. |
| ETSI EN 319 411-1 | Policy and security requirements for TSPs issuing certificates — General requirements. |
| ETSI EN 319 412-1 | Certificate Profiles — Overview and common data structures. |
| ETSI EN 319 421 | Policy and security requirements for TSPs issuing time-stamps. |
| ETSI EN 319 422 | Time-stamping protocol and electronic time-stamp profiles. |
| ETSI EN 319 102-1 | Procedures for Creation and Validation of AdES Digital Signatures — Part 1. |
| Regulation (EU) 910/2014 | eIDAS — electronic identification and trust services for electronic transactions. |
| Regulation (EU) 2024/1183 | eIDAS 2 — amending Regulation (EU) 910/2014 (EUDI Wallet). |
| Regulation (EU) 2024/1689 | The AI Act. |
| Directive (EU) 2022/2555 | NIS2 — Network and Information Security Directive 2. |

### 3.2 Informative references

| Identifier | Title |
| --- | --- |
| IETF RFC 9116 | A File Format to Aid in Security Vulnerability Disclosure (`security.txt`). |
| ETSI TS 119 312 | Cryptographic Suites — algorithm catalogue for TSP services. |
| ETSI TS 119 402 | Trust Service Provider Practice Statement structure. |
| ETSI TS 119 432 | Protocols for Remote Digital Signature Creation. |
| ETSI TS 119 461 | Policy and security requirements for identity proofing of trust service subjects. |
| ISO/IEC 27001:2022 | Information security management systems — Requirements. |
| NIST IR 8547 | Transition to Post-Quantum Cryptographic Standards. |
| C2PA 2.x | Coalition for Content Provenance and Authenticity — Content Credentials. |
| Regulation (EU) 2016/679 | GDPR — General Data Protection Regulation. |
| EATF AEP profile v1 | `docs/specs/aep-profile-v1.md` (normative for the profile itself). |
| EATF TSPS v1 | `docs/legal/TSPS.md` (operational practice statement). |
| EATF EN 319 401 self-assessment | `docs/legal/etsi-en-319-401-self-assessment.md`. |
| EATF threat model | `docs/legal/threat-model.md` (Phase 1.6). |

---

## 4. Definitions, symbols and abbreviations

### 4.1 Definitions

For the purposes of the present document, the following terms apply. Where a term is also defined by ETSI EN 319 401 or eIDAS, the present definition restates the established meaning without modification and is given here for the convenience of the reader.

**AEP / Aletheia Evidence Package.** A `.aep` binary container, defined normatively in `docs/specs/aep-profile-v1.md`, that bundles canonicalised payload, hybrid signatures, RFC 3161 timestamp token, public keys and verification metadata into a single offline-verifiable artefact.

**Agent.** A URN-identified logical actor bound to a subscriber tenant via a manifest. Not an independent subject under eIDAS or this profile; identity proofing is transitive through the subscribing tenant.

**Attest mode.** A signing-service entry point that produces an AEP carrying not only the integrity envelope but also a per-rule policy evaluation report.

**Canonicalisation.** The deterministic byte-level normalisation procedure applied to the payload and the metadata document before hashing.

**Canonical bytes.** The output of applying the canonicalisation algorithm `eatf-canonical-1` to the source payload and metadata; the input to both the SHA-256 hash and the digital signatures.

**Dispute registry.** The out-of-band annotation mechanism (clause 6.7) by which a subscriber or relying party records that a particular attestation should not be relied upon, in lieu of a CRL-style revocation.

**Evidence package.** Synonym of AEP.

**Hybrid signature.** A pair of digital signatures over the same SHA-256 digest, produced by two independent algorithms (RSA-4096 PKCS#1 v1.5 and ML-DSA-65), each of which independently verifies the integrity of the payload.

**ML-DSA-65.** Module-Lattice-Based Digital Signature Algorithm, FIPS 204, parameter set Dilithium3 (security level 3, equivalent to AES-192).

**Non-qualified trust service.** A trust service that does not bear the qualified-trust-service legal presumptions of eIDAS Articles 25, 35 or 42 but that nonetheless provides cryptographic and operational integrity guarantees, voluntarily aligned where practical with the qualified baseline.

**Policy (attestation policy).** A named, versioned set of rules evaluated during an `attest` call against the agent's input, output, references and contextual metadata.

**Profile-of-profile.** A specialisation that constrains, but does not extend incompatibly, an underlying ETSI signature profile for a specific use case.

**Relying party.** Any party that receives an AEP and runs a conformant verifier against it.

**Sign mode.** A signing-service entry point that produces an AEP carrying the integrity envelope only, with no policy evaluation.

**Subscriber / tenant.** A legal entity holding a contractual relationship with the issuing TSP and authorised to call `sign` or `attest` on its own behalf.

**Timestamp token.** An RFC 3161 `TimeStampToken` ASN.1 structure carrying a time-stamping authority's signed assertion that a particular hash existed at a particular moment.

**TSA (Time-Stamping Authority).** An RFC 3161-conformant time-stamping service. May be qualified under eIDAS Article 42 (a "qualified TSA") or non-qualified.

### 4.2 Symbols

No mathematical symbols beyond standard cryptographic notation are used in the present document.

### 4.3 Abbreviations

| Abbreviation | Expansion |
| --- | --- |
| AEP | Aletheia Evidence Package |
| AES | Advanced Encryption Standard |
| ASiC | Associated Signature Container |
| BFF | Backend-For-Frontend |
| C2PA | Coalition for Content Provenance and Authenticity |
| CAdES | CMS Advanced Electronic Signatures |
| CMS | Cryptographic Message Syntax |
| CRL | Certificate Revocation List |
| EATF | Enterprise Agent Trust Framework |
| eIDAS | Electronic Identification, Authentication and Trust Services |
| EN | European Norm (ETSI) |
| ETSI | European Telecommunications Standards Institute |
| FIPS | Federal Information Processing Standard |
| GDPR | General Data Protection Regulation |
| HSM | Hardware Security Module |
| JCS | JSON Canonicalisation Scheme |
| JTC 21 | Joint Technical Committee 21 (CEN-CENELEC AI standardisation) |
| LAMPS | Limited Additional Mechanisms for PKIX and SMIME (IETF WG) |
| ML-DSA | Module-Lattice-Based Digital Signature Algorithm |
| NIS2 | Network and Information Security Directive 2 |
| OID | Object Identifier |
| PKCS | Public Key Cryptography Standards |
| PQC | Post-Quantum Cryptography |
| QTSP | Qualified Trust Service Provider |
| RFC | Request for Comments (IETF) |
| RoPA | Record of Processing Activities |
| RSA | Rivest–Shamir–Adleman cryptosystem |
| SoD | Segregation of Duties |
| TR | Technical Report (ETSI) |
| TS | Technical Specification (ETSI) |
| TSA | Time-Stamping Authority |
| TSP | Trust Service Provider |
| TSPS | Trust Service Practice Statement |
| URN | Uniform Resource Name |
| XAdES | XML Advanced Electronic Signatures |

---

## 5. Technical specification

This clause is the technical body of the present document. It restates the AEP v1 profile at the level of detail appropriate to a TR audience and references `docs/specs/aep-profile-v1.md` for the byte-exact normative text. Where this clause and the normative spec diverge, the normative spec governs.

### 5.1 Container format

An AEP v1 package is a **ZIP archive** in the PKZIP family, *store* or *deflate*. Entries live at the archive root; nested directories are forbidden in v1. The choice of a flat ZIP — rather than a tagged binary container, ASiC-E or proprietary — reflects three pragmatic considerations: universal tooling (every OS includes a ZIP reader), forward compatibility (unknown entries are ignored), and hash discipline (the SHA-256 is computed over a separately stored canonical-bytes entry, so integrity does not depend on ZIP-level determinism).

Maximum uncompressed size is 10 MiB in v1, matching the public verifier endpoint's request-body limit. Default file extension is `.aep`; implementations MAY accept `.zip` where the manifest is unambiguous.

### 5.2 File manifest

A v1 package MUST contain the following REQUIRED entries at the archive root, case-sensitive:

- `response.txt` — the textual payload attested. UTF-8, no byte-order mark, line endings preserved.
- `canonical.bin` — the canonical byte sequence from clause 5.3. Hash and signatures are computed over this entry.
- `hash.sha256` — lower-case hex SHA-256 of `canonical.bin` (64 ASCII chars, optional trailing LF).
- `signature.sig` — Base64 RSA-4096 PKCS#1 v1.5 signature (inner digest SHA-256) over `canonical.bin`.
- `public_key.pem` — PEM `SubjectPublicKeyInfo` of the RSA-4096 public key.
- `metadata.json` — the metadata document of clause 5.4.
- `timestamp.tsr` — Base64 RFC 3161 `TimeStampToken`. The token is issued over the SHA-256 of the ASCII hex string in `hash.sha256` (the `messageImprint` re-hashes that ASCII representation), not over `canonical.bin` directly. This matches the `freetsa.org` and DigiCert conventions; see clause 5.6.

When the issuing TSP advertises PQC support (`ai.aletheia.signing.pqc-enabled=true`, EATF default since Phase 1.9), these OPTIONAL entries become REQUIRED:

- `signature_pqc.sig` — Base64 ML-DSA-65 signature over the same `canonical.bin`.
- `pqc_public_key.pem` — PEM-encoded ML-DSA-65 public key. PEM rather than X.509-wrapped pending LAMPS Working Group stabilisation of ML-DSA OIDs (clause 10, open issue (c)).
- `pqc_algorithm.json` — `{"algorithm":"ML-DSA-65","oid":"2.16.840.1.101.3.4.3.18","level":3}`. The OID is NIST's FIPS 204 reference value; provenance discussed in clause 10.

Three further entries are OPTIONAL: `policy_coverage.json` (per-rule attestation report in `attest` mode), `agent_manifest.json` (manifest snapshot at signing time), and `disclosure.json` (Article 50 transparency metadata, from Phase 2.6).

A verifier MUST accept unknown additional entries and MUST refuse a package missing any REQUIRED or conditionally-REQUIRED entry.

### 5.3 Canonicalisation algorithm `eatf-canonical-1`

The canonicalisation algorithm produces the bytes that are hashed and signed. It is identified by the literal string `eatf-canonical-1` and is recorded in the `canonicalisation` field of `metadata.json`.

The procedure is:

1. Compute the **canonical JSON form** of `metadata.json` per RFC 8785. All object members are sorted by Unicode codepoint of the key; no insignificant whitespace is emitted; numbers are serialised per ECMA-404 with no trailing zeros; strings use only the JSON-required escapes; the result is UTF-8 without byte-order mark.
2. Read the bytes of `response.txt` verbatim. The signing service MUST NOT silently normalise line endings; any prior normalisation MUST be documented in the `canonicalisation` field.
3. Concatenate, in order: the UTF-8 bytes of `response.txt`, a single LF byte (0x0A) separator, the canonical JSON form from step 1.
4. The result of step 3 is `canonical.bin`. SHA-256 is computed over those bytes; both RSA and ML-DSA signatures are computed over those bytes.

A verifier MUST refuse a package if the recomputed canonical bytes do not match the embedded `canonical.bin` entry. The algorithm is deterministic across implementations, language runtimes and platforms; the test vectors of clause 7.2 fix it byte-exactly.

### 5.4 Metadata schema

`metadata.json` is the primary integration surface for downstream tooling. Annex A carries the full JSON Schema. REQUIRED fields:

- `schema` — fixed URN `urn:eatf:spec:aep:metadata:1.0`.
- `attestation_id` — ULID, format `att_<ULID>`.
- `uuid` — RFC 4122 UUIDv4 alias.
- `tenant_id_hash` — SHA-256 hex of the issuing tenant's numeric id. The raw id is **never** transmitted; an auditor with directory access can verify the binding, an unrelated reader cannot enumerate tenants.
- `agent_id` — the URN of the issuing agent.
- `model` — the model identifier supplied by the agent.
- `policy_id`, `policy_version` — the policy evaluated in `attest` mode (omitted or `urn:eatf:policy:none` in `sign` mode).
- `created_at` — RFC 3339 UTC.
- `canonicalisation` — `eatf-canonical-1`.
- `hash_algorithm` — `SHA-256`.
- `rsa_key_id`, `pqc_key_id` — opaque signing-key identifiers.
- `tsa_url` — the TSA that issued `timestamp.tsr`.
- `issuer` — `{name, url, tsps_version}` pinning the practice-statement version under which the package was issued.

Unknown fields MUST be tolerated.

### 5.5 Cryptographic primitives

The v1 catalogue aligns with ETSI TS 119 312 for classical primitives and FIPS 204 for the PQC primitive:

- **Hash.** SHA-256 (FIPS 180-4).
- **Classical signature.** RSA-4096 with PKCS#1 v1.5 padding (RFC 8017 §8.2.1) over SHA-256 DigestInfo. PSS padding is reserved for v2.
- **Post-quantum signature.** ML-DSA-65 (FIPS 204, Dilithium3, security level 3). The package format is additive: a future v2 may carry SLH-DSA (FIPS 205) or a successor as a third entry without breaking v1 verifiers.
- **Timestamp.** RFC 3161 with SHA-256 message imprint, TSA cert RSA-2048 or stronger per RFC 3161 and EN 319 422.

Verifier obligations: (a) confirm embedded `hash.sha256` matches SHA-256 of `canonical.bin`; (b) verify `signature.sig` (RSA) and, when PQC entries are present, `signature_pqc.sig` (ML-DSA) against the embedded public keys; (c) verify the RFC 3161 token. A v1 conformant verifier rejects on any single failure. Open issue (d) of clause 10 discusses whether a future profile should relax to "accept on either signature".

### 5.6 RFC 3161 timestamp profile

The TSA token is issued over the **ASCII hex string** of `hash.sha256` rather than over the raw bytes of `canonical.bin`. This indirection has two operational advantages: a smaller TSA-request payload, and conformity with the convention adopted by `freetsa.org` and most commercial TSAs.

Verifier procedure: decode `timestamp.tsr` from Base64; parse as an ASN.1 `TimeStampToken` per RFC 3161 §2.4.2; confirm `messageImprint.hashAlgorithm` is the SHA-256 OID `2.16.840.1.101.3.4.2.1`; compute SHA-256 over the ASCII contents of `hash.sha256` (recommended without trailing newline); confirm equality with `messageImprint.hashedMessage`; verify the TSA's signature against the certificate carried in the token, anchored to a TSP-published trust store (for EATF: `https://eatf.eu/.well-known/tsa-cert.pem`).

For the EATF non-qualified internal TSA, `genTime` is the backend wall clock with a ±2 s drift bound. For a qualified TSA, the qualified TSA's `genTime` and accuracy attributes apply per EN 319 422.

### 5.7 Profile-of-profile relationship to existing ETSI signature formats

AEP is a **specialisation**, not a competitor:

- **EN 319 122-1 (CAdES).** AEP could be expressed as a CAdES `SignedData` with `signed-attributes` carrying the AI-specific metadata. AEP v1 does not adopt CAdES at the wire level because its audience includes lawyers, auditors and procurement teams without ASN.1 tooling; a flat ZIP with PEM and JSON is inspectable in a text editor. A future v2 MAY define an equivalent CAdES profile.
- **EN 319 132-1 (XAdES).** XAdES targets XML payloads; AEP payloads are textual. XAdES re-expression is feasible but has not been requested.
- **EN 319 162-1 (ASiC).** ASiC defines a ZIP-based container structurally similar to AEP. The principal divergence is the metadata document and the absence of a `META-INF/` directory in AEP v1 — chosen so that a verifier cannot confuse an AEP for an ASiC-E and apply the wrong validation procedure. A future v2 MAY define an ASiC-E-compatible packaging.
- **EN 319 102-1.** The procedures for creation and validation of AdES digital signatures apply *mutatis mutandis* to the RSA leg. The ML-DSA leg is not covered because the standard predates FIPS 204; alignment is among the open issues in clause 10.

The intent is that a reader familiar with EN 319 122 / 132 / 162 should recognise AEP as a relative of those formats with three additions — AI-attestation metadata, hybrid classical+PQC signing, and canonical-bytes-first integrity — and zero subtractions.

### 5.8 Revocation model — dispute registry rather than CRL

AEP does **not** support CRL-style revocation. The structural reason: an evidence package is a self-contained signed record at time T and cannot be cryptographically "untrusted" without invalidating the signing key for every other package signed by that key. Revoking a single attestation has no clean cryptographic analogue.

Instead, the issuing TSP operates a **dispute registry** — an out-of-band annotation, keyed on `attestation_id`, queryable at a public endpoint (for EATF: `GET /api/public/attestations/{id}/status`). The original AEP is unmodified; the dispute is consulted alongside it.

In the event of signing-key compromise, the issuing TSP publishes the affected key fingerprint at its public notices URL (for EATF: `https://eatf.eu/security#notices`) and recommends that relying parties treat all packages signed with that key as disputed *en bloc*. Detailed procedure: `docs/legal/TSPS.md` §5.7. Any future TR or TS proposing CRL-based revocation for AI-attestation packages must demonstrate why this model is insufficient.

---

## 6. Conformance

The present clause defines the conformance taxonomy and the test-vector regime under which a conformance claim can be verified.

### 6.1 Conformance levels

Three levels are defined.

**Strict v1.** An AEP package is strictly conformant if it satisfies every clause of `docs/specs/aep-profile-v1.md` marked REQUIRED for v1, including PQC entries when the issuing TSP advertises PQC support. A strict emitter produces only strict packages; a strict verifier accepts every strict package and rejects every non-conformant package.

**Transitional v1.** An AEP package is transitionally conformant if it satisfies every REQUIRED v1 clause but lacks PQC entries. Transitional conformance exists to support pre-Phase-1.9 EATF deployments and early implementers without FIPS 204 libraries. Transitional verifiers accept both transitional and strict packages. AEP v2 will not carry this level forward.

**Non-conformance.** A package is non-conformant if it (a) lacks any REQUIRED entry, (b) fails canonical-bytes recomputation, (c) fails either signature verification, (d) fails RFC 3161 token verification, or (e) carries an unrecognised `metadata.schema` value.

### 6.2 Test vectors

Normative vectors live at `backend/src/test/resources/fixtures/`, in three sub-directories:

- `valid/` — positive vectors: minimum-form, PQC-enabled, and maximal-form with `policy_coverage.json` / `agent_manifest.json` plus unknown future-extension entries.
- `tampered/` — negative vectors, one mutation per vector (hash mismatch, RSA-sig mismatch, ML-DSA-sig mismatch, TSA-token mismatch, metadata corruption, missing REQUIRED entry, unknown `hash_algorithm`). A conformant verifier rejects each with a documented error code.
- `forward-compat/` — vectors carrying unknown ZIP entries or unknown metadata fields; v1 verifiers MUST accept them.

The vectors are signed by an EATF "Publications" tenant; signing-key fingerprints are mirrored at `https://github.com/tyche-institute/eatf-trust-anchors`, so a reviewer can confirm the tree has not been silently mutated.

### 6.3 Conformance assertion

A claim of "AEP v1 strict conformance" implies passing every relevant vector. Claims are non-self-certifying: claimants are encouraged to publish test-run logs and hashes of the vector tree exercised, so an independent reviewer can replicate.

---

## 7. Implementation notes

### 7.1 Reference verifier

The authoritative reference verifier is at `backend/src/main/java/ai/aletheia/verifier/`, MIT-licensed. The shaded Maven profile `-Pverifier` produces a self-contained executable JAR with Bouncy Castle and BCPQC. Requirements: a Java 21 runtime. The verifier operates entirely offline.

Contract: given a `.aep` and a (possibly empty) trust store for the TSA certificate, return `OK` with parsed metadata, or a structured `Reject` with a documented error code (`HASH_MISMATCH`, `SIG_MISMATCH_RSA`, `SIG_MISMATCH_PQC`, `TSA_TOKEN_INVALID`, `METADATA_SCHEMA_UNKNOWN`, `REQUIRED_ENTRY_MISSING`, `CANONICAL_BYTES_MISMATCH`). A `RejectAdvisory` channel reports non-fatal observations (e.g. unknown metadata field) without rejecting.

### 7.2 WebAssembly verifier (Phase 1.20)

A WASM build is scheduled for Phase 1.20, produced from the same Java source via TeaVM or GraalVM Native Image. Two engineering risks are tracked: (i) BCPQC's ML-DSA implementation must compile to WASM without native code paths — prototyped in `sdks/eatf-verifier-ts/`; (ii) the WASM build must produce byte-identical canonical-bytes computations as the Java build, enforced by a cross-implementation test harness against the vector tree.

### 7.3 Other planned implementations

Python (`sdks/python-sdk/`) and TypeScript verifiers are planned for Phase 1.20; a Go verifier for Phase 2. None of these is normative; the Java reference verifier is the source of truth and divergence is treated as a bug in the divergent implementation.

### 7.4 Signing-side considerations

The reference signing service is in `backend/src/main/java/ai/aletheia/evidence/EvidencePackageServiceImpl.java`. The ledger entry recording an attestation is written **before** the AEP is returned to the caller, so that an in-flight crash cannot leave a relying party with a verifiable AEP that the issuing TSP has no record of having issued. A future profile clarification may codify this explicitly.

---

## 8. Security considerations

The detailed threat model lives at `docs/legal/threat-model.md` (Phase 1.6). The present clause summarises the threats most relevant to a profile reviewer.

### 8.1 Signing-key compromise

The most consequential threat. Because every AEP carries the public key inline, a relying party cannot detect compromise from the AEP alone and depends on the dispute registry and public notices channel (clause 5.8). Mitigations are operational: HSM-backed signing from EATF Phase 1.9, four-eyes key ceremonies, an independently mirrored trust-anchors timeline at `https://github.com/tyche-institute/eatf-trust-anchors`. The hybrid regime mitigates the case where one algorithm is broken without the other.

### 8.2 TSA single point of failure

A compromised or unreliable TSA degrades the temporal property without degrading integrity. The profile permits per-tenant external TSA configuration so relying parties with high temporal assurance can require an eIDAS Article 42 qualified TSA anchor. Multi-TSA timestamping is on the v2 roadmap.

### 8.3 Supply-chain risk

Bouncy Castle and BCPQC are reference-verifier dependencies. Mitigations: version pinning, Dependabot CVE alerts, CodeQL static analysis, Sigstore Cosign signing of releases (Phase 1.11). The WASM build (Phase 1.20) inherits these considerations.

### 8.4 Algorithm deprecation

NIST IR 8547 sketches a deprecation timeline for classical RSA signatures around 2035. The hybrid regime is the operational answer: when RSA is deprecated the TSP stops emitting `signature.sig` while verifiers continue to accept legacy packages on either signature. When ML-DSA is itself succeeded, a v2 introduces a third signature entry without breaking v1 verifiers.

### 8.5 Downgrade attacks

An attacker may supply a package that omits PQC entries even though the issuing TSP advertised PQC support, hoping a permissive verifier accepts the classical signature alone. Mitigation: a `metadata.json` carrying `pqc_key_id` signals PQC entries were issued; a strict verifier refuses a package that names `pqc_key_id` but lacks `signature_pqc.sig` / `pqc_public_key.pem`.

### 8.6 ZIP-format ambiguities

"ZIP confusion" attacks rely on central-directory vs local-header divergence. Mitigation: canonical bytes are computed over `response.txt` and `metadata.json` contents directly, not over the ZIP structure. Any divergence affects parseability but not integrity — a verifier that fails to extract a REQUIRED entry rejects the package; one that extracts a tampered entry recomputes the canonical bytes and detects the tampering.

---

## 9. Privacy considerations

The privacy properties are deliberately conservative.

**What is in the package.** `response.txt` carries the textual output the subscribing tenant chose to attest. `metadata.json` carries `tenant_id_hash`, the agent URN, the model identifier, policy id/version, timestamps, key identifiers and the issuer block. `agent_manifest.json` (when present) carries a snapshot of the agent description as registered at signing time.

**What is not in the package.** The raw tenant numeric id is **never** transmitted. An auditor with tenant-directory access can verify the binding between a `tenant_id_hash` and a tenant; an unrelated reader cannot enumerate tenants. No customer PII is added by the issuing TSP. If a subscribing tenant places PII in `response.txt`, that is a tenant-side decision governed by the subscriber agreement and any DPA; the issuing TSP is a GDPR Article 28 processor for that payload (see `docs/legal/TSPS.md` §9.4).

**Pseudonymisation.** The `agent_id` URN is opaque; relying parties MUST NOT assume it encodes human-readable meaning. The URN-to-description binding lives in the agent manifest snapshot, consistent with GDPR Article 4(5).

**Right-to-be-forgotten constraints.** Because the AEP is integrity-bound, an issued AEP cannot be retroactively modified to remove personal data. Mitigation: subscriber agreements advise tenants not to attest PII unless the data-protection regime allows the resulting cryptographic retention. The TSP's server-side copy is subject to a 5-year retention window (`docs/legal/TSPS.md` §5.5); the offline-verifiable property of in-the-wild copies does not depend on this retention.

**Data minimisation.** The metadata fields are the minimum needed for offline verification plus an audit trail to the issuing tenant. The `disclosure.json` entry (Phase 2.6) is OPTIONAL and populated only when the tenant opts into Article 50 transparency disclosure for a specific attestation.

---

## 10. Open issues

The present document is offered for ESI Working Group review. The contributing organisation invites comment on the following open issues; this list is not exhaustive.

**(a) X.509 wrapping versus raw PEM for ML-DSA public keys.** AEP v1 carries the ML-DSA public key as raw PEM `BEGIN PUBLIC KEY` / `END PUBLIC KEY` blocks because the IETF LAMPS Working Group draft on ML-DSA OIDs has not yet stabilised at submission time. A v2 of the profile will switch to X.509-wrapped distribution once the LAMPS draft reaches a stable OID assignment. Working Group comment is sought on whether the present raw-PEM approach is acceptable for an interim profile or whether the WG would prefer that AEP v1 wait for the LAMPS draft to stabilise.

**(b) Alignment with C2PA Content Credentials.** The Coalition for Content Provenance and Authenticity publishes a manifest format for provenance metadata in media assets. There is a partial overlap with AEP for the case where the AI-attested payload is itself a media artefact (image, audio, video). Working Group comment is sought on whether an AEP-to-C2PA mapping should be normatively specified in a future revision, or whether the two formats should remain independent.

**(c) ML-DSA OID stability.** The OID `2.16.840.1.101.3.4.3.18` recorded in `pqc_algorithm.json` is the value used by NIST in the FIPS 204 reference implementation. The IETF LAMPS Working Group is finalising the OIDs for use in X.509 contexts; if those OIDs diverge from the NIST values, AEP will need to choose a canonical reference. The contributing organisation favours the IETF LAMPS values when they stabilise, but invites WG comment.

**(d) Required-both versus permitted-either verifier semantics.** AEP v1 strict conformance requires that a verifier check both the RSA and the ML-DSA signature when both are present. An alternative reading would be that a verifier may pass either signature, on the rationale that the hybrid regime exists precisely to survive the breakage of one primitive. Working Group comment is sought on which reading should be normative for a future revision.

**(e) Relationship to ETSI TS 119 432 remote signing.** EATF operates closer to a remote signing service than to a classical CA. ETSI TS 119 432 specifies the protocols for remote digital signature creation; a future TS-level deliverable could specify the AEP profile as the output format of a TS 119 432-conformant remote signing service for AI-attestation use cases. Working Group comment is sought on whether such alignment is desirable.

**(f) Qualified-TSA timestamp anchoring at the profile level.** AEP v1 permits per-tenant external TSA configuration but does not mandate qualified-TSA timestamping. The AI Act's record-keeping obligations under Article 12 do not require qualified timestamping; the question is whether a future high-risk profile of AEP should require it for Annex III use cases.

---

## 11. Annexes

### Annex A (informative) — JSON Schema for `metadata.json`

The following schema is informative; the normative definition is in `docs/specs/aep-profile-v1.md` clause 5. The schema is supplied here so that a reviewer can validate sample metadata documents without checking out the EATF repository.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:eatf:spec:aep:metadata:1.0",
  "title": "AEP metadata.json (v1.0)",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "schema", "attestation_id", "uuid", "tenant_id_hash",
    "agent_id", "model", "created_at",
    "canonicalisation", "hash_algorithm",
    "rsa_key_id", "tsa_url", "issuer"
  ],
  "properties": {
    "schema":          { "const": "urn:eatf:spec:aep:metadata:1.0" },
    "attestation_id":  { "type": "string", "pattern": "^att_[0-9A-HJKMNP-TV-Z]{26}$" },
    "uuid":            { "type": "string", "format": "uuid" },
    "tenant_id_hash":  { "type": "string", "pattern": "^[0-9a-f]{64}$" },
    "agent_id":        { "type": "string", "format": "uri" },
    "model":           { "type": "string" },
    "policy_id":       { "type": "string" },
    "policy_version":  { "type": "string" },
    "created_at":      { "type": "string", "format": "date-time" },
    "canonicalisation":{ "const": "eatf-canonical-1" },
    "hash_algorithm":  { "const": "SHA-256" },
    "rsa_key_id":      { "type": "string" },
    "pqc_key_id":      { "type": "string" },
    "tsa_url":         { "type": "string", "format": "uri" },
    "issuer": {
      "type": "object",
      "required": ["name", "url", "tsps_version"],
      "properties": {
        "name":         { "type": "string" },
        "url":          { "type": "string", "format": "uri" },
        "tsps_version": { "type": "string", "pattern": "^urn:eatf:tsps:" }
      }
    }
  }
}
```

### Annex B (informative) — Example test vector

The following is an example metadata document, structurally consistent with the minimum-form valid vector in `backend/src/test/resources/fixtures/valid/`. The accompanying `response.txt`, `canonical.bin`, signatures and TSA token are byte-exact in the repository and are not reproduced here.

```json
{
  "schema": "urn:eatf:spec:aep:metadata:1.0",
  "attestation_id": "att_01HXY8K9V0RS7E4M3PQR8A2BC5",
  "uuid": "0c45db8d-1bf2-4f7e-9c8f-f7e2c5f7f76e",
  "tenant_id_hash": "f3a1c79b2e8d4ff1d6b3a09cce4b7a23a8e92fbc1b0d5a8e92fbc1b0d5a8e92f",
  "agent_id": "urn:eatf:agent:medical-assistant-7a3c",
  "model": "gpt-4o-2025-08-06",
  "policy_id": "atap-basic",
  "policy_version": "1.0",
  "created_at": "2026-05-12T11:23:45Z",
  "canonicalisation": "eatf-canonical-1",
  "hash_algorithm": "SHA-256",
  "rsa_key_id": "kid_rsa_2026-01",
  "pqc_key_id": "kid_mldsa65_2026-01",
  "tsa_url": "https://freetsa.org/tsr",
  "issuer": {
    "name": "EATF.eu",
    "url": "https://eatf.eu",
    "tsps_version": "urn:eatf:tsps:1.0"
  }
}
```

For the byte-exact canonical form of the above, the receiving verifier applies the algorithm of clause 5.3: members sorted by codepoint, no insignificant whitespace, ECMA-404 number serialisation, UTF-8 without byte-order mark. The canonical bytes of the example are concatenated with the UTF-8 bytes of `response.txt` and an LF separator to form `canonical.bin`, over which SHA-256 produces `hash.sha256`. The full byte-by-byte vector is reproduced in `backend/src/test/resources/fixtures/valid/minimum-form/`.

### Annex C (informative) — Liaison report with CEN-CENELEC JTC 21

CEN-CENELEC JTC 21 (Artificial Intelligence) is the European standardisation body responsible for harmonised AI Act standards. EATF intends to submit, in Phase 2.12, a liaison report describing the AEP profile to the JTC 21 working groups responsible for AI Act record-keeping (Article 12) and transparency (Article 50) horizontal standards. Objectives:

- Inform JTC 21 of an operationally deployed evidence-package format that addresses the same regulatory clauses from the trust-service side.
- Explore whether the AEP profile (or a derivative) could be referenced as one acceptable means of compliance with the eventual JTC 21 record-keeping harmonised standard.
- Coordinate terminology between the ESI workstream and the JTC 21 AI-systems workstream — in particular for overlapping but non-identical terms ("provenance", "attestation", "evidence", "audit trail").
- Gather feedback on the dispute-registry revocation model, novel for both AI-attestation and trust-service practice.

The full liaison report is not yet drafted; this annex is a placeholder. The drafted report will be published as `docs/specs/etsi-tr-aep-jtc21-liaison.md` and referenced from a revision of the present TR.

---

## Revision history

| Version | Date | Author | Summary |
| ------- | ---- | ------ | ------- |
| 0.1-draft | 2026-05-12 | EATF maintainer team | Initial working draft for ESI workstream submission, aligned with AEP v1.0-draft of the same date. Comment period open through 2026-08-12. |

**End of working draft.**

*Comments to `security@aletheia.ai` through 2026-08-12. After that date a comment-disposition log will be appended as a further annex.*


