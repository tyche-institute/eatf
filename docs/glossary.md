# Glossary (stub)

**Status:** stub for v0.1.0.

## Terms

**AEP — Agent Evidence Package.** A self-contained, offline-verifiable
ZIP artefact documenting an agent's actions and outputs. See
[`aep-profile.md`](./aep-profile.md).

**Agent attestation.** A signed claim about an agent (identity,
capability, operator mandate). Carried inside an AEP under
`attestations/`. See [`attestation-profile.md`](./attestation-profile.md).

**eIDAS.** Regulation (EU) 910/2014, as amended by Regulation
(EU) 2024/1183 ("eIDAS 2"). EATF is **not** a trust service under
eIDAS Article 3(16).

**Issuer.** The operator entity whose private key signed the
package's manifest. Identified by the issuer certificate carried
under `certs/issuer.pem`.

**JCS — JSON Canonicalization Scheme.** IETF RFC 8785. Defines the
byte sequence to which JSON documents are normalised before
signing. EATF uses JCS for all JSON canonicalisation.

**ML-DSA-65.** NIST FIPS 204 module-lattice digital signature
algorithm, parameter set 65. Used in EATF alongside RSA-4096 for
hybrid post-quantum signing.

**Private CA.** A certificate authority operated by an EATF
deployment for issuing agent certificates. Not a public trust
service; verifiers trust the private CA only if they have been
configured with its root anchor.

**QEAA — Qualified Electronic Attestation of Attributes.** eIDAS
Article 3(45). Issued by Qualified Trust Service Providers. EATF
agent attestations are **not** QEAAs.

**QTSP — Qualified Trust Service Provider.** A TSP that has been
granted qualified status under eIDAS by a national supervisory body
and appears on an EU/EEA Trusted List. Tyche Institute is **not** a
QTSP.

**TSA — Time-Stamping Authority.** An RFC 3161 timestamping server.
EATF packages carry an RFC 3161 TimeStampResp under
`timestamps/manifest.tsr` to bind the manifest signature to a trusted
wall-clock time.

**Trust anchor.** A self-signed certificate or public key that a
verifier has been pre-configured to trust. Verifiers maintain
separate anchor sets for issuer CAs and for time-stamping authorities.

**VC — Verifiable Credential.** W3C VC Data Model 2.0. The data
model used for the `agent.vc.json` attestation record inside an AEP.

## Status-label legend

For the four standards-relationship labels (IMPLEMENTED, ALIGNED,
REFERENCED, ADDRESSED), see the legend section of
[`architecture.md`](./architecture.md).
