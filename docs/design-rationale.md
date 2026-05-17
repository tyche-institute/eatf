# Design rationale

**Status:** v0.1 (2026-05-17). Stable. Reflects the design
decisions in force for the v0.1 line.

This document captures the *why* behind EATF's design choices.
Each section names a decision, then explains the alternative
considered, the trade-off, and the constraint that determined
the choice.

For the *what*, see [`aep-profile.md`](aep-profile.md) (wire
format) and [`architecture.md`](architecture.md) (layered
structure). For *what we deliberately don't do*, see
[`../ROADMAP.md`](../ROADMAP.md) §"Explicit non-goals".

## 1. Offline verification

**Decision:** A verifier with only the package bytes and a
configured trust anchor must be able to assert authenticity,
integrity, and timeliness — no network call required.

**Alternative considered:** A REST-based verification API where
the deployment hosts a `/verify` endpoint that the relying party
calls.

**Why we chose offline:**

- **Auditor workflow fit.** Auditors frequently need to verify
  packages produced years earlier or by deployments that have
  since gone offline. An online-only design fails immediately
  when the deployment goes away; an offline design keeps
  working as long as the package + trust anchor exist.
- **Independence from operator availability.** An online verifier
  is a single point of failure controlled by the operator. If
  the operator's API is down, the auditor's evidence is unreadable.
  This is exactly the trust shape the project was built to avoid.
- **Independence from operator goodwill.** An online verifier can
  silently lie (return `verify=true` for arbitrary input). Offline
  cryptography cannot.
- **10-year audit horizon.** AI Act Annex IV record-keeping
  obligations can extend to a decade. We optimise for the worst
  case (operator gone, network gone, lawyer with the file and a
  CD-ROM verifier).

**Cost accepted:** Revocation must be expressed inside the package
(or trusted at verification time from independently-distributed
mirrors); the verifier must hold trust anchors locally.

## 2. Hybrid classical + post-quantum signing

**Decision:** Every signed package SHOULD carry both a classical
signature (RSA-PSS or ECDSA-P256) and an ML-DSA-65 post-quantum
signature. Verifiers MUST validate the classical signature and
MUST validate the post-quantum signature when present.

**Alternative considered:** Wait for the post-quantum standards
(NIST FIPS 204/205/206) to be widely supported and switch in one
step.

**Why hybrid:**

- **No flag day.** Hybrid lets us ship ML-DSA-65 today without
  waiting for every downstream verifier to upgrade. Old verifiers
  validate the classical signature; PQC-aware verifiers validate
  both.
- **Damage bound on either-side cryptanalysis.** If either suite
  is later found weak, the other still stands. This is the
  rationale for "both classical AND post-quantum", not
  "classical OR post-quantum".
- **NIST guidance alignment.** FIPS 204 explicitly contemplates
  hybrid deployment during the transition window.

**Cost accepted:** Larger packages (ML-DSA signatures are ~2-3 KB
each); modest additional CPU on the verifier path; the operator
maintains two key pairs instead of one.

## 3. RSASSA-PKCS1-v1_5 (legacy) classical suite as default

**Decision:** The v0.1 reference packages use RSASSA-PKCS1-v1_5
with SHA-256 (RFC 8017 §8.2), not the modern RSA-PSS.

**Alternative considered:** RSA-PSS as the default classical
suite.

**Why PKCS1-v1_5:**

- **Java reference compatibility.** The historical Java reference
  implementation emits PKCS1-v1_5. v0.1 keeps both forms
  verifiable to preserve a clean migration path for deployments
  that already have PKCS1-v1_5 packages in their archives.
- **Web Crypto direct support.** `crypto.subtle.verify("RSASSA-
  PKCS1-v1_5", ...)` is universally available; PSS handling in
  some browsers historically required workarounds.

**Mitigation:** The verifier in `lib/src/rsa.ts` also supports
RSA-PSS via the same Web Crypto interface. A future release can
switch the default; we will introduce a profile-version bump
(`urn:eatf:spec:aep:1.1` or `2.0`) when it does, so existing
deployments are not silently invalidated.

## 4. ML-DSA-65 selection over ML-DSA-44 / 87 / SLH-DSA

**Decision:** ML-DSA-65 (NIST FIPS 204 parameter set 65; ~3293-byte
signatures; ~1952-byte public keys; ~4032-byte private keys).

**Alternatives:**

- **ML-DSA-44** (smaller; weaker security category 2 vs. 3).
- **ML-DSA-87** (larger; stronger security category 5).
- **SLH-DSA** (FIPS 205; hash-based; very large signatures
  ~7 KB+ but minimal cryptanalytic assumptions).

**Why ML-DSA-65:**

- **Security/size balance.** Category 3 is comparable to
  AES-192, well above any predicted post-quantum break.
- **Library maturity.** `@noble/post-quantum` ships ML-DSA-65
  with audited verification path. SLH-DSA support is similarly
  available but signatures are ~2.5× larger.
- **Forward path.** If category 3 turns out to be marginal, the
  format already allows hybrid + bumping to ML-DSA-87 without a
  protocol redesign — bump the suite URN, ship updated
  `pqc_public_key.pem`, keep the package envelope intact.

## 5. JCS canonicalisation over alternatives

**Decision:** RFC 8785 JSON Canonicalization Scheme for JSON
content that gets signed.

**Alternatives:**

- Bespoke canonicalisation rules.
- COSE (CBOR-based signed objects).
- ANSI X9 / W3C VC's c14n.

**Why JCS:**

- **Single-author specification.** RFC 8785 is short, fully
  specified, and easy to implement in any language.
- **Library availability.** `lib/src/canonical.ts` is ~75 lines
  for full JCS; equivalent in Python (`canonicaljson`), Go
  (`gowebpki/jcs`), Rust (`serde_jcs`).
- **No CBOR dependency.** COSE is excellent but adds a binary
  encoding step that breaks human inspection of the
  `canonical.bin` file. We optimise for "you can look at the
  bytes and roughly understand them".

## 6. RFC 3161 timestamps over alternatives

**Decision:** RFC 3161 `TimeStampToken` embedded as
`timestamp.tsr`. TSA choice is left to the deployment.

**Alternatives:**

- Operator wall-clock + signed assertion (no third-party
  timestamp).
- Blockchain-anchored timestamps (Bitcoin, Ethereum).
- Roughtime (Cloudflare's broadcast-time protocol).

**Why RFC 3161:**

- **Auditor familiarity.** RFC 3161 is the de-facto standard for
  qualified electronic timestamps under eIDAS. Auditors know what
  it means. Blockchain timestamps require additional explanation
  every time.
- **Vendor breadth.** Multiple TSAs are publicly available
  (freetsa.org, DigiCert, Sectigo, GlobalSign, GeoTrust). The
  operator chooses one; verifiers chain TSA certificates to roots
  they've pre-configured.
- **No infrastructure dependency.** No coin, no blockchain, no
  network outside the TSA request.

**Cost accepted:** The verifier must understand ASN.1 / CMS to
parse the token. pkijs handles it; the dependency is modest.

## 7. Private CA for agent identity, not a public QTSP

**Decision:** Agent certificates inside an EATF deployment are
signed by a private CA operated by the deployment, not by a
public QTSP under eIDAS.

**Why private CA:**

- **eIDAS positioning.** Issuing agent certificates from a public
  QTSP would entangle EATF with eIDAS qualified-trust-service
  semantics, which do not apply cleanly to AI agents and which
  would change the project's regulatory footing.
- **Operator choice.** Deployments that want public QTSP
  involvement can layer one on top (e.g. bind the operator's
  organisational certificate from a public CA to the deployment's
  private CA root). EATF the framework stays neutral.
- **Cost.** Public QTSP issuance per agent is impractical at the
  scale individual deployments need (thousands of agents).

**Alternative for verifiers:** A verifier MAY refuse any package
whose `public_key.pem` does not chain to a trust anchor it has
explicitly configured. This is the right default for high-stakes
verification; the framework provides the primitive, the verifier
configures the policy.

## 8. Open specification, not a managed service

**Decision:** The wire format, schemas, conformance vectors,
verifier, and signer are published under Apache 2.0. There is no
proprietary verifier. There is no required runtime relationship
with Tyche Institute.

**Alternative considered:** A managed verification service with a
free tier and paid enterprise tier.

**Why open:**

- **Trust assumption symmetry.** A managed-service verifier
  shifts the trust assumption from "do I trust the operator who
  signed this?" to "do I trust the operator AND the verification
  service?". That's strictly worse for the relying party.
- **Operator independence.** Anyone can implement an independent
  verifier in any language from the published spec and test
  vectors alone (see `lib-python/` planned in v0.2.0 and `lib-go/`
  in v0.3.0). The conformance contract — "produce the right
  `verify=true|false` for every vector in `test-vectors/`" — is
  the only thing implementers need.
- **Long-term durability.** A managed service can vanish; an
  Apache 2.0 spec + verifier do not.

## 9. DCO sign-off, not a Contributor License Agreement

**Decision:** Contributions accepted under the Developer
Certificate of Origin (`git commit -s`). No CLA.

**Why DCO:**

- **Apache 2.0 already grants the project broad rights including a
  patent grant.** A CLA adds marginal legal protection at
  significant overhead — legal review, signature collection, friction
  for casual contributors.
- **Convention alignment.** The Linux kernel, Kubernetes, Docker,
  GitLab, and many other large projects use the DCO. Following the
  convention reduces friction for contributors who have already
  signed off elsewhere.
- **CI-enforceable.** The DCO check is a single grep on commit
  messages; no humans in the loop. See `.github/workflows/ci.yml`.

## 10. No hosted registry, no marketplace

**Decision:** EATF the framework deliberately does not operate a
central registry of agents, a public-key directory, a marketplace,
or any centralised discovery layer. Verifiers use trust anchors
they configure themselves; discovery (if any) is the operator's
choice of mechanism.

**This decision has its own essay-in-progress** at
`~/projects/tyche-research-vault/outlines/on-the-crossroads-marketplace-vs-distributed-trust.md`
in the maintainer's research vault, expected to land as a public
piece in 2026. Short version:

- A registry would dissolve the offline-verifiable design
  property by putting a third party in the trust path.
- It would conflict with the project's eIDAS positioning (a
  catalogue of "approved" agents looks structurally identical to
  the EU Trusted List of QTSPs).
- It would re-introduce the structural-power asymmetry that
  EATF's flat deployment model is designed to avoid.
- It would create a surveillance surface that the offline design
  specifically avoids generating.
- It would be a gravity well toward managed-service, which
  CONTRIBUTING.md explicitly declines.

The distributed-trust pattern (public-key history mirrors,
operator-configured trust anchors, conformance vectors, no
discovery layer at framework level) replaces what a registry
would have provided.

## Related documents

- [`aep-profile.md`](aep-profile.md) — the wire-format these
  decisions produced.
- [`architecture.md`](architecture.md) — how the decisions map
  to code structure.
- [`threat-model.md`](threat-model.md) — what each decision
  defends against.
- [`glossary.md`](glossary.md) — terminology for the concepts
  used here.
- [`../ROADMAP.md`](../ROADMAP.md) — what's coming next and
  what's deliberately out of scope.
