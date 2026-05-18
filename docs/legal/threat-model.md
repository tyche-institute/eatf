# Threat model — EATF reference implementation

> **Operator update (2026-05-14).** The operator entity for the EATF
> reference implementation is **Tyche Institute** (Estonian non-profit,
> registration in progress). EATF stands for **Agent Trust Framework**.
> This is a self-published research document representing the
> maintainer's analysis. It does not constitute a formal commitment,
> regulatory filing, or legal opinion. EATF is **not** a trust service
> under eIDAS Article 3(16) and Tyche Institute does not operate as a
> Trust Service Provider; the threat model below refers to EATF as a
> *cryptographic attestation pipeline*, not as a trust service.

**Version: 1.0-draft, dated 2026-05-12 (operator-entity revision 2026-05-14), comment period open**

Contact: `security@aletheia.ai` for private disclosure (see `SECURITY.md`).
This document is a public artefact. It will be revised after auditor review
and after every roadmap step that meaningfully changes the trust boundary.

---

## 1. Executive summary

EATF (Agent Trust Framework) is a **cryptographic attestation pipeline
for AI agent actions** — it is **not** an eIDAS trust service. A
customer's autonomous agent or human operator performs an action;
EATF canonicalises the request, evaluates it against policy, signs
the resulting evidence record with both RSA-4096 and ML-DSA-65
(post-quantum), anchors the signature time in an RFC 3161 timestamp,
and appends a tamper-evident block to a per-tenant hash-chained
ledger. The output is an `.aep` evidence package that an external
auditor can verify **offline**, using a published JAR, without ever
calling an EATF deployment.

That gives the reference implementation two simultaneous postures:
it is an **early-stage open-source project** (small maintainer team,
no managed-HSM yet, no SOC 2, single region in any reference
deployment), and it is a **long-lived cryptographic attestation
producer** whose evidence outputs must remain verifiable for years
after any single deployment of EATF disappears. The threat model must
take both seriously.

The Phase 0 commit (`c64bb81`) closed five audit-critical defects that an
external review would have flagged immediately: a permissive default JWT
secret accepted in production, a database connection that did not require
TLS, SUPER_ADMIN tenant overrides without an HMAC, audit events that could
land with `tenant_id = NULL`, and an unbounded rate-limit map. All five
now fail-close on production boot or are bounded in memory. The mint-flow
race on the ledger is gone. The TSA Docker image is pinned. Policy
unavailability raises HTTP 503 instead of silently fail-opening.

After Phase 0, the **biggest residual risks** an auditor should focus on are:

1. **Signing keys live on the filesystem.** Private RSA-4096 and ML-DSA-65
   keys are read from `AI_ALETHEIA_PQC_KEY_PATH`. A host compromise leaks
   them. **Mitigation: Phase 1.9** — managed HSM (AWS CloudHSM or Azure
   Dedicated HSM) via PKCS#11.
2. **The TSA is a single point of failure.** `RealTsaServiceImpl` calls one
   configured URL with a 30s timeout and no fallback chain. **Mitigation:
   Phase 1.24** (SK ID partnership) and a primary/secondary/tertiary
   fallback documented in Phase 1.27.
3. **Solo-operator insider risk.** There is currently one principal with
   production access. **Mitigation: Phase 1.4** termination plan, public
   key history mirrored at a third-party, plus Phase 2.14 SOC 2 Type II.
4. **No automated key rotation.** A leaked key today cannot be rolled
   without a manual ceremony. **Mitigation: Phase 1.10** —
   `PqcKeyRotationService`, ledger blocks tagged with `key_id`, verifier
   trust-chain over historical keys.
5. **Rate limiting is per-process, not edge-wide.** Caffeine-bounded after
   Phase 0, but a distributed abuser can still consume Cloudflare and BFF
   capacity. **Mitigation: Phase 1.11** — Redis-backed limiter and
   Cloudflare rate-limiting rules.

**How to read this document.** Section 2 fixes vocabulary and STRIDE scope.
Section 3 walks each trust boundary. Section 4 is the bulk: a STRIDE
threat table per major component, each row pointing at the code that
implements the mitigation. Section 5 covers cross-cutting risks that don't
belong to one component. Section 6 lists what we accept as residual. Section
7 maps every `planned` mitigation to the phase that will close it. An
auditor or procurement officer should read sections 1, 5 and 6 first, then
spot-check section 4 for the components most relevant to their concern,
then check section 7 against the roadmap in
`docs/legal/etsi-en-319-401-self-assessment.md` (Phase 1.2).

---

## 2. Scope and method

### 2.1 STRIDE

We use STRIDE for category cover. Every row in section 4 is tagged with one
or more of:

- **S** — Spoofing identity (an attacker pretends to be another principal).
- **T** — Tampering with data in flight or at rest.
- **R** — Repudiation (a principal denies an action they performed, or
  cannot prove an action they performed).
- **I** — Information disclosure (leakage of secrets or tenant data).
- **D** — Denial of service.
- **E** — Elevation of privilege (a principal gains rights they should not
  have, including cross-tenant access).

We deliberately do **not** use CVSS scoring at this stage. CVSS is calibrated
for product CVEs, not for trust-service threat modelling, and the operator
is small enough that a `low/medium/high` residual-risk column is more
useful than a contested numeric score. We will revisit once an
ETSI EN 319 401 self-assessment is published (Phase 1.2).

### 2.2 In scope

- The Spring Boot 3.5 / Java 21 backend
  (`backend/src/main/java/ai/aletheia/`).
- The Next.js BFF and Auth.js session layer (`frontend/`, including
  `frontend/middleware.ts`).
- The Cloudflare Pages / Workers edge that fronts the BFF.
- The PostgreSQL database, including the per-tenant `tenant_id` filters
  on JPA entities and the V215 audit-events constraint.
- The cryptographic signing pipeline: canonicalisation → SHA-256 →
  RSA-4096 + ML-DSA-65 → RFC 3161 TSA.
- The per-tenant hash-chained ledger
  (`backend/src/main/java/ai/aletheia/ledger/AletheiaLedgerService.java`).
- The `.aep` evidence package and the offline verifier
  (`backend/src/main/java/ai/aletheia/verifier/`).
- Identity surfaces: tenant, agent, end user, API key (`alth_live_…`),
  Spring API JWT, BFF mint key, `X-BFF-Sig` HMAC.
- The TSA dependency.
- Java / npm supply chain plus the pinned TSA Docker image.

### 2.3 Out of scope

- Customer LLM providers (OpenAI, Anthropic, Google, etc.). The customer
  trusts them; EATF only signs evidence about what the customer's agent
  decided to do. A compromise of a customer's LLM provider does not
  invalidate prior signed evidence — that is precisely why the trust
  service exists.
- Third-party MCP hosts that embed `aletheia-mcp-server`. Their threat
  surface is covered in `partner-integrations/aletheia-mcp-server/THREAT_MODEL.md`.
- Customer-side key custody for their organisation's keys. EATF only
  manages **its own** signing keys; a customer key cabinet is the
  customer's problem.
- Hardware-level attacks on the cloud provider (Hetzner, Cloudflare).
  These are the cloud provider's threat model; we trust their SOC 2
  attestations.
- Side-channel attacks on the host CPU. Out of scope until HSM
  integration (Phase 1.9), at which point keys never reach a general-
  purpose CPU.

---

## 3. Trust boundaries

Five boundaries are crossed by a typical request. Each is enforced by
specific code; each defends against a specific set of STRIDE categories.

```
[Browser / agent] --(TLS, OAuth or API key)-->  [Cloudflare edge]
       (B1: untrusted internet)
[Cloudflare edge] --(authenticated origin pull)--> [Next.js BFF]
       (B2: edge --> BFF)
[Next.js BFF] --(BFF mint key + X-BFF-Sig HMAC)--> [Spring Boot backend]
       (B3: BFF --> backend)
[Backend] --(JDBC over TLS, parameterised queries, tenant filter)-->
       (B4: backend --> PostgreSQL)             [PostgreSQL]
[Backend] --(HTTPS, RFC 3161 TSQ over POST)-->    [TSA (DigiCert /
       (B5: backend --> TSA)                         SK ID future)]
```

**B1 — internet to Cloudflare.** TLS termination at Cloudflare with
managed certificates, plus Cloudflare's bot management and basic WAF.
Defends primarily against transport-layer spoofing (S) and tampering (T)
and absorbs the first wave of denial-of-service (D). Cloudflare's edge
also implements coarse rate-limiting in front of `/api/**`.

**B2 — Cloudflare to BFF.** The BFF (Next.js, Auth.js / NextAuth) checks
that the session cookie is one of the expected names before allowing
non-public routes (`frontend/middleware.ts:38-70`). Public routes (`/`,
`/landing`, `/compliance`, `/verify`, `/pricing`, `/for-auditors`, demo
pages) are explicitly enumerated; any non-listed route without a session
cookie redirects to `/auth/signin`. The list of public paths is the
audit-relevant inventory of unauthenticated entry points.

**B3 — BFF to backend.** Two-layer authentication:

1. A short-lived Spring API JWT (HS256) signed with
   `AI_ALETHEIA_JWT_SECRET`, minted by `/api/auth/credentials` or by the
   BFF's `GET /api/auth/session/bff` endpoint (which itself requires the
   shared `AI_ALETHEIA_BFF_MINT_KEY`). Validated in
   `JwtAuthenticationFilter`
   (`backend/src/main/java/ai/aletheia/security/JwtAuthenticationFilter.java`).
2. Any SUPER_ADMIN tenant override via `X-Tenant-Id` or `X-Tenant-Key`
   must additionally carry an HMAC `X-BFF-Sig` over `X-BFF-Ts` and the
   tenant headers, signed with the same `AI_ALETHEIA_BFF_MINT_KEY`. The
   HMAC is verified by `BffHeaderSigner`
   (`backend/src/main/java/ai/aletheia/security/BffHeaderSigner.java`) and
   `TenantInterceptor`. Required in production
   (`ai.aletheia.security.bff-header-hmac.required=true` in
   `application-prod.properties`), off in tests.

Defends elevation of privilege (E) — a stolen session cookie alone cannot
mint a tenant override — and spoofing (S) of internal headers.

**B4 — backend to database.** JDBC over TLS, enforced at boot:
`DatabaseTlsValidator` refuses to start the application in `prod` profile
unless `SPRING_DATASOURCE_URL` includes `sslmode=require` or
`verify-full`. All queries go through JPA (parameterised, no string
concatenation). Tenant isolation is enforced by Hibernate filters keyed
on `tenant_id`; cross-tenant queries are blocked at the repository layer
and audited via `AuditEventService`, which (post-Phase 0) throws
`IllegalStateException` if a tenant-scoped event ever attempts to save
without a tenant context. The V215 migration re-asserts
`audit_events.tenant_id NOT NULL` as a defence-in-depth.

**B5 — backend to TSA.** `RealTsaServiceImpl` POSTs an
`application/timestamp-query` to a configured TSA URL with a 30-second
HTTP timeout (`RealTsaServiceImpl:39`). The response is parsed via
BouncyCastle's `TimeStampResponse` and validated (`status != 0`, token
present). The TSA itself is a trust anchor — we delegate timestamp
authenticity to a qualified provider (DigiCert today, SK ID future per
Phase 1.24). The Docker image for the local mock TSA used in
docker-compose is pinned to `ghcr.io/digicert/timestamp-authority:v0.13.1`
(`docker-compose.yml`, Phase 0 step 0.12).

---

## 4. Per-component threat tables

Each table is keyed by component. Columns: **Threat**, **STRIDE**,
**Mitigation** (with code reference), **Residual** (low / medium / high)
and **Status** (mitigated / partial / accepted / planned). Planned rows
cite the phase that closes them.

### 4.1 Identity surfaces

The platform has six identity surfaces that an attacker could spoof or
elevate. Audit-critical to understand all six.

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.1.1 | JWT forgery via weak `AI_ALETHEIA_JWT_SECRET` (documented default, short string) | S, E | `JwtSecretValidator` refuses to boot in `prod` profile if secret is a dev placeholder or shorter than 32 bytes (`backend/src/main/java/ai/aletheia/config/JwtSecretValidator.java`); HS256 with `Authorization: Bearer` validated by `JwtService` (`backend/src/main/java/ai/aletheia/security/JwtService.java`). | Low | Mitigated (Phase 0) |
| 4.1.2 | Session-cookie theft (XSS, malware on auditor laptop) lets attacker reach internal routes | S, E | BFF sets `__Secure-` cookie names; `frontend/middleware.ts:38-47` requires the cookie before any non-public route; backend additionally requires the API JWT to mutate state. | Medium | Partial — XSS hardening tracked Phase 1 |
| 4.1.3 | API key theft (`alth_live_…`) lets attacker call any tenant operation as the key owner | S, E | API keys are 32+ byte random, prefixed `alth_live_`; stored hashed (BCrypt) in `partner_api_keys`; revocable; tied to a tenant in JWT auth filter; `ApiKeyService.authenticate` returns `Optional<Auth>` so a stolen-but-revoked key never produces an authentication object (`backend/src/main/java/ai/aletheia/security/apikey/ApiKeyService.java`). Phase 0 fixed a cross-tenant scoping bug where `DEFAULT_TENANT_ID=1` was being silently applied when the chain mis-ordered. | Medium | Partial — key rotation + per-key scoping by route is Phase 1.10 |
| 4.1.4 | BFF mint key (`AI_ALETHEIA_BFF_MINT_KEY`) leak — attacker can mint arbitrary API JWTs by `userId` | S, E | Shared secret never sent to the browser; only the Next.js server reads it; backend rejects calls to `/api/auth/session/bff` without exact-match secret; HMAC for tenant overrides binds key to specific header set + timestamp (`BffHeaderSigner.java`); replay window short. | Medium | Partial — moves to per-request short-lived JWT in Phase 1.17 |
| 4.1.5 | `X-BFF-Sig` HMAC bypass — attacker calls backend with spoofed `X-Tenant-Id` to read another tenant's data | E, I | `TenantInterceptor` (`backend/src/main/java/ai/aletheia/security/TenantInterceptor.java`) plus `BffHeaderSigner.verify(...)` require valid `X-BFF-Sig` + `X-BFF-Ts` for any override; replay window is 5 minutes; required in prod, off in test. | Low | Mitigated (Phase 0) |
| 4.1.6 | OAuth account-takeover via stale email → new Google account with same address | S | `AI_ALETHEIA_OAUTH_AUTO_PROVISION=false` in prod prevents creation of new users from OAuth alone; existing accounts only. | Low | Mitigated (config) |
| 4.1.7 | Agent identity spoofing — attacker tells backend their agent is a different agent | S, R | Every signed evidence record names the agent by tenant-scoped agent UUID; ledger and `.aep` package both carry the agent id; verifier checks the agent signature against the registered agent public key. | Low | Mitigated |
| 4.1.8 | Invite signup abuse to create VIEWER accounts in the default tenant | E | Requires `AI_ALETHEIA_INVITE_SECRET` to be set; without it, `POST /api/public/register-invite` is disabled; with it, only VIEWER role in default tenant. | Low | Partial — invite secret rotation tracked in operator runbook |

### 4.2 Signing pipeline

The canonical signing flow is: caller request → JSON canonicalisation
(RFC 8785 / JCS) → SHA-256 digest → RSA-4096 signature → ML-DSA-65
signature → RFC 3161 timestamp over the concatenated digest → ledger
block. Code path:
`backend/src/main/java/ai/aletheia/crypto/impl/`.

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.2.1 | Canonicalisation ambiguity — same logical payload produces different bytes between clients | T, R | RFC 8785 JCS canonicalisation deterministic by spec; round-trip tests in `EvidencePackageServiceImplTest`. | Low | Mitigated |
| 4.2.2 | RSA-4096 broken by future quantum adversary | T, R | Hybrid signing: every record carries **both** RSA-4096 and ML-DSA-65 signatures. Verifier accepts a record iff both verify. ML-DSA-65 is NIST-selected post-quantum standard. | Low | Mitigated |
| 4.2.3 | ML-DSA-65 superseded by next-generation PQC standard | T, R | Crypto-agility is partial today: each signed block records an algorithm identifier but the verifier hard-codes the supported algorithm set. Algorithm-rotation path planned for Phase 1.10. | Medium | Planned (Phase 1.10) |
| 4.2.4 | Signing private keys read from filesystem; host compromise → key leak | I, S, T | Today: `AI_ALETHEIA_PQC_KEY_PATH` points at filesystem; permissions enforced by deployment scripts; never committed to git. Honest gap: a root-on-host attacker reads them. Planned: AWS CloudHSM / Azure Dedicated HSM via PKCS#11 (Phase 1.9). | **High** | Planned (Phase 1.9) |
| 4.2.5 | TSA timestamp forged — attacker controls the TSA URL or MITM | T, R | TSA URL configured statically; HTTPS for any non-local TSA; TSA's qualified certificate is verified by BouncyCastle's `TimeStampResponse` validation; Phase 1.24 brings in a qualified TSP partner whose certificate is anchored in EU Trust Lists. | Low | Partial — qualified TSP in Phase 1.24 |
| 4.2.6 | Signing oracle abuse — attacker reaches `/api/v1/sign` endpoint and signs arbitrary payloads | E, R | All sign endpoints require authenticated tenant context (`SecurityConfig`); rate-limited by `ApiRateLimitFilter`; signed payload always carries the agent id, so a stolen-key signature still names a specific agent that can be revoked. | Medium | Partial — endpoint-level allowlist Phase 1.6 |

### 4.3 Evidence package (.aep) and offline verifier

The `.aep` file is a self-contained zip with the canonical payload, the
RSA + ML-DSA signatures, the TSA token, the public keys, and a chain
proof. Offline verifier:
`backend/src/main/java/ai/aletheia/verifier/EvidenceVerifierImpl.java`,
shipped as a shaded JAR for downstream auditors.

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.3.1 | Forged `.aep` package: attacker swaps payload, keeps original signatures | T, R | Verifier recomputes the digest from canonical payload and compares against signature subject; mismatch fails verification. | Low | Mitigated |
| 4.3.2 | Malicious `.aep` with attacker-supplied public keys | S, T | Verifier resolves agent and tenant public keys from a published key directory (publicly mirrored — see Phase 1.4 termination plan), not from the package itself. | Medium | Partial — public mirror named in Phase 1.4 |
| 4.3.3 | `.aep` upload exploits in `/verify` public route — zip-bomb, path-traversal | D, T | Size cap on multipart upload (10 MB); zip entry name sanitisation; verifier runs in a memory-bounded path. | Medium | Partial — WASM-in-browser verifier in Phase 1.20 removes server attack surface entirely |
| 4.3.4 | Verifier produces false positive due to crypto-library CVE | T, R | BouncyCastle is the only signing library; pinned via Maven; Dependabot watches; verifier is a shaded JAR with reproducible build (planned). | Medium | Partial — reproducible build in Phase 1.12 |
| 4.3.5 | Schema drift — newer `.aep` files cannot be verified by older verifier JAR | R | `.aep` carries a version field; verifier rejects unknown versions explicitly. `AEP-profile-v1.md` (Phase 1.5) is the published schema contract. | Low | Planned (Phase 1.5) — schema doc |

### 4.4 Per-tenant hash-chained ledger

`AletheiaLedgerService.checkAndMintForTenant`
(`backend/src/main/java/ai/aletheia/ledger/AletheiaLedgerService.java`)
appends a block to a per-tenant chain: every block stores the SHA-256 of
its payload **and** the SHA-256 of the previous block. The chain is
sealed by daily roll-ups timestamped via TSA.

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.4.1 | Operator silently rewrites history by editing rows | T, R | Hash chain: rewriting any block breaks the next block's `prev_hash`; daily TSA-timestamped roll-up provides external time anchoring; database backups are append-only on the operator side. | Low | Mitigated |
| 4.4.2 | Cross-tenant chain collision: two tenants' blocks interleave; one tenant sees the other's history | I, E | Each tenant has an independent chain identified by `tenant_id`; Hibernate tenant filter applied at repository layer; verifier reads only blocks of the named tenant. | Low | Mitigated |
| 4.4.3 | Concurrent mint race — two threads append simultaneously and `prev_hash` corrupts | T, R | `ReentrantLock` per tenant in `AletheiaLedgerService.checkAndMintForTenant` (Phase 0); single-writer guarantee at the JVM. Multi-node deployment will need a PostgreSQL advisory lock or a queue — tracked Phase 1.11. | Medium | Partial — multi-node Phase 1.11 |
| 4.4.4 | Genesis-block forgery: attacker creates a fake "tenant zero" block at install time | T | Genesis block is written once at tenant provisioning by `TenantProvisioningService`, signed and timestamped; subsequent blocks chain to its hash; tenant provisioning requires SUPER_ADMIN with HMAC. | Low | Mitigated (Phase 0) |
| 4.4.5 | Ledger truncation — operator drops the tail | T, R | Daily TSA-timestamped roll-up commits the chain tip to an external timestamp; the next time anyone verifies, the missing tail is detected. Phase 1.18 ships a public roll-up viewer. | Medium | Partial — public roll-up viewer Phase 1.18 |

### 4.5 Multi-tenant isolation

`TenantContext`, `TenantInterceptor`, JPA `@Filter(tenant_id)` and the
V215 NOT NULL constraint on `audit_events.tenant_id` together form the
isolation layer.

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.5.1 | Repository query forgets to apply tenant filter, returns cross-tenant rows | I, E | Default tenant filter enabled globally on Hibernate Session; service-layer code reviewed; integration tests fan out per-tenant. Phase 1 will add a Spotless rule "no service method without tenant param". | **High** | Partial — compiler-level enforcement Phase 1-2 |
| 4.5.2 | Background job runs without tenant context, writes to wrong tenant | T, E | `AuditEventService.saveEvent` throws `IllegalStateException` when no tenant set (Phase 0); V215 migration enforces NOT NULL at the database; scheduled jobs explicitly pass tenant id from configuration. | Medium | Partial — Phase 1 sweeps remaining schedulers |
| 4.5.3 | SUPER_ADMIN inadvertently mutates another tenant | E | `X-Tenant-Id` / `X-Tenant-Key` override requires `X-BFF-Sig` HMAC (Phase 0); audit event records the override; operator runbook requires two-person review for any prod override. | Low | Mitigated |
| 4.5.4 | OAuth multi-tenant claim mismatch — user lands in wrong tenant on sign-in | E | Tenant resolved from `tenant_users` join, not from OAuth claim; `AI_ALETHEIA_OAUTH_AUTO_PROVISION=false` in prod. | Low | Mitigated |

### 4.6 TSA dependency

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.6.1 | TSA outage halts the signing pipeline | D | `RealTsaServiceImpl` has 30s timeout and surfaces a `TimestampException`; callers see a 503 via `PolicyExceptionAdvice` pattern; **fail-closed**: no record is committed without a timestamp. | **High** | Planned (Phase 1.27 — primary/secondary/tertiary fallback chain) |
| 4.6.2 | TSA returns a non-qualified timestamp because EATF accidentally points at FreeTSA | T, R | Configured TSA URL is part of operator runbook; production deployment uses DigiCert; SK ID partnership (Phase 1.24) brings EU-qualified. | Medium | Partial — Phase 1.24 |
| 4.6.3 | TSA cert expires; old `.aep` packages fail verification later | R | Verifier uses TSA cert from the token itself plus a published trust list; expiry of the issuing CA is anticipated and handled by EU Trust List rotation. | Low | Mitigated |
| 4.6.4 | DNS hijack of TSA hostname — attacker injects malicious response | T | HTTPS to the TSA; TSA response is signed and verified by BouncyCastle, not just trusted by transport. | Low | Mitigated |
| 4.6.5 | Local mock TSA used in production by misconfiguration | T, R | `ai.aletheia.tsa.mode=real` required for any non-dev profile; mock TSA bean is conditional on `mock` value; deployment scripts assert mode in CI. | Low | Mitigated |

### 4.7 Supply chain

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.7.1 | Compromised Maven dependency injects backdoor at build time | T, E | Maven `pom.xml` pins every direct dependency; Dependabot watches; planned reproducible build for verifier (Phase 1.12); SBOM published per release (Phase 1.13). | **High** | Partial — Phase 1.12 / 1.13 |
| 4.7.2 | Compromised npm dependency in BFF leaks session cookie / mint key | T, I | `package-lock.json` committed; Dependabot; `AI_ALETHEIA_BFF_MINT_KEY` is server-side env, never in client bundle; CSP planned Phase 1.19. | **High** | Partial — Phase 1.19 |
| 4.7.3 | Compromised Docker base image | T | TSA image pinned to `v0.13.1` (Phase 0); backend base image is `eclipse-temurin:21-jre`, digest-pinned in CI build (Phase 1.13). | Medium | Partial — full digest pinning Phase 1.13 |
| 4.7.4 | GitHub Actions secret leak via PR from fork | I, E | Workflows that touch secrets are gated on the `main` branch + `pull_request_target` not used for prod-secret jobs; deployment secrets are environment-scoped in GitHub. | Low | Mitigated |
| 4.7.5 | Typo-squatted dependency added inadvertently | T | Code review on `pom.xml` and `package.json` diffs is mandatory per `CODEOWNERS`. | Medium | Accepted (manual control) |

### 4.8 Frontend (Next.js BFF + Cloudflare Workers)

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.8.1 | `AI_ALETHEIA_BFF_MINT_KEY` leaks into client bundle | I, E | Read only via `process.env` in server-only files; Next.js build fails if a server-only env appears in a client component (eslint rule + manual review). | Low | Mitigated |
| 4.8.2 | NextAuth session token tampered to elevate role | E | JWT-style session token signed by NextAuth with `NEXTAUTH_SECRET`; backend never trusts the BFF's role claim — it re-resolves role from the database per request. | Low | Mitigated |
| 4.8.3 | Public-route bypass — attacker hits an internal route directly and gets a 200 without auth | E, I | `frontend/middleware.ts` explicitly enumerates public paths (`isPublicPath`); anything else redirects to `/auth/signin`; backend additionally rejects without JWT. Two-layer defence. | Low | Mitigated (Phase 0) |
| 4.8.4 | CSRF on state-changing routes | T | All state-changing routes require `Authorization: Bearer` JWT; cookies alone do not authenticate to `/api/**`; backend has `csrf.disable()` because CSRF is structurally impossible without cookie-authenticated mutation. | Low | Mitigated |
| 4.8.5 | XSS via reflected query parameter in `/verify` upload UI | T, I | `AepDropZone` does not reflect filenames into HTML; rendered output is the verifier's structured JSON report; React's default escaping holds. CSP header in Phase 1.19. | Medium | Partial — CSP Phase 1.19 |
| 4.8.6 | Cloudflare Workers script tampering at the edge | T | Workers are deployed from CI with signed releases; Cloudflare dashboard is MFA-protected; deploy audit log is reviewed weekly. | Medium | Accepted (operator control) |

### 4.9 Operational denial-of-service

| # | Threat | STRIDE | Mitigation | Residual | Status |
|---|---|---|---|---|---|
| 4.9.1 | Burst of `/api/**` traffic exhausts backend threads | D | `ApiRateLimitFilter` (Bucket4j) per-IP token bucket; Caffeine-bounded cache (max 100k entries, expireAfterAccess=15min) so the limiter itself cannot OOM the JVM (Phase 0). | Medium | Partial — Redis-backed limiter Phase 1.11 |
| 4.9.2 | One tenant exhausts the database connection pool | D | HikariCP with bounded pool size; backpressure surfaces as 503; planned per-tenant connection-pool quotas (Phase 2). | Medium | Partial — Phase 2 |
| 4.9.3 | Long-running TSA call blocks request thread | D | 30s HTTP timeout in `RealTsaServiceImpl`; Phase 1.27 introduces async timestamp queue so the TSA call no longer blocks the HTTP request path. | Medium | Planned (Phase 1.27) |
| 4.9.4 | Audit-log disk exhaustion | D | Planned automated archival to S3-class cold storage in Phase 1.15. Until then, ops alerts on disk utilisation. | Medium | Planned (Phase 1.15) |
| 4.9.5 | Crash-loop on policy unavailability | D | `PolicyExceptionAdvice` maps `PolicyNotFoundException` to HTTP 503 (`policy_registry_unavailable`); the request fails closed but the process does not exit. | Low | Mitigated (Phase 0) |

---

## 5. Cross-cutting risks

### 5.1 Supply-chain compromise

A successful supply-chain attack against Maven Central, npm or a Docker
base image bypasses every other control. Today we rely on lockfiles,
Dependabot, code review on dependency changes, and TSA image pinning
(Phase 0 step 0.12). Honest gap: no reproducible builds yet for the
verifier JAR, no signed SBOM yet, no in-toto attestation. Phase 1.12
(reproducible verifier build) and Phase 1.13 (SBOM and digest-pinned
container images) close this gap. Until then we accept the risk
explicitly: a determined adversary who compromises a transitive
dependency can compromise the signing process.

### 5.2 Key compromise

The platform has four classes of long-lived secret:

- **RSA-4096 signing key.** Currently filesystem-backed; HSM-bound in
  Phase 1.9.
- **ML-DSA-65 signing key.** Same custody story; same Phase 1.9 fix.
  Algorithm rotation tracked in Phase 1.10.
- **`AI_ALETHEIA_JWT_SECRET`.** HS256 secret for short-lived API JWTs.
  Phase 0 enforces minimum length and refuses dev defaults in prod.
  Rotation today is a manual restart with a new value; a stale-window of
  ~5 minutes is acceptable because tokens are short-lived.
- **`AI_ALETHEIA_BFF_MINT_KEY`.** Shared between Next.js server and
  Spring Boot backend; protects the BFF→backend trust boundary. Same
  rotation story as JWT secret. Phase 1.17 moves this to a per-request
  short-lived JWT minted by NextAuth and verified by Spring with a
  rotating keyset.

Key compromise of either signing key is **catastrophic for previously
unsigned future records but does not invalidate previously signed
records** — old `.aep` packages remain verifiable against the
contemporaneous public key, which is mirrored externally (Phase 1.4
termination plan). This is the entire reason for the ledger + TSA
design.

### 5.3 HSM provider compromise

Once Phase 1.9 lands, EATF depends on AWS CloudHSM or Azure Dedicated
HSM. A compromise of the HSM provider is in scope for cross-cutting
risk. Mitigations: HSM tenancy is single-customer (not shared); EATF
will hold the wrapping keys in escrow with a separate cloud account;
Phase 1.10 key rotation can roll quickly. We accept that a
nation-state-level compromise of AWS/Azure is outside our threat model.

### 5.4 Insider risk

EATF today has **one principal** with production access. This is the
single largest residual risk and we name it openly. Mitigations in
flight:

- **Phase 1.4 termination plan** — public document committing to: (a)
  offline verifier remains operable without EATF, (b) public keys
  mirrored on a named third-party site, (c) algorithms and `.aep`
  schema published, (d) escrowed backups.
- **Phase 1.14 SOC 2 Type I** kicked off via Vanta / Drata / Strike
  Graph; Phase 2.14 escalates to Type II.
- **Phase 1.7 two-person rule** for any production change touching
  signing keys or tenant data.
- **Public ledger roll-up** (Phase 1.18): the daily timestamped chain
  tip is published, so a silent rewrite would be visible to any
  third-party watcher.

### 5.5 Legal and jurisdiction

EATF is operated from Estonia (h2oatlas OÜ) and hosts customer evidence
in the EU. The AI Act has extraterritorial reach (Art. 2), so the
threat surface includes legal compulsion under foreign jurisdictions:

- A US court order against an EATF subprocessor (Cloudflare) cannot
  reach plaintext customer data because the BFF does not see signed
  payloads; the backend (Hetzner) is the data plane.
- A court order against EATF itself to surrender signing keys would,
  under Phase 1.9 HSM custody, require physical seizure of HSM
  modules. The signing operation is logged on the ledger; tampering
  would be visible after the fact.
- A court order to **insert** a fake evidence record would conflict
  with the public ledger roll-up: a third-party watcher would see the
  chain advancing without a matching public verifier output.

These are partial defences and we acknowledge them as such. They are
not legal immunity — they are evidence-preservation guarantees.

---

## 6. Residual risks accepted

In the interest of an honest document, the following are risks we know
we do not fully mitigate today.

1. **Filesystem-backed signing keys.** Until Phase 1.9, the RSA-4096 and
   ML-DSA-65 private keys can be read by anyone with root access to the
   backend host. Rationale: HSM integration costs €10-15k/yr and Phase 1
   is the right window to take that on. Compensating controls: hardened
   host, restricted SSH, no shared accounts, audit log on the host.
2. **No automated key rotation.** Phase 1.10 closes this. Today, the
   operator runbook documents a manual ceremony but it has not been
   exercised in production.
3. **TSA single point of failure.** A primary/secondary/tertiary chain
   is Phase 1.27. Until then a TSA outage stops new signing. We accept
   this because **fail-closed is the right behaviour for a trust
   service** — a record without a qualified timestamp is not evidence.
4. **No SOC 2 or ISO 27001 yet.** Phase 1.14 (Type I), Phase 2.14
   (Type II), Phase 2.15 (ISO 27001 kickoff). Today the documentation is
   the artefact, not the attestation.
5. **Solo operator.** Two-person rule (Phase 1.7) is an
   organisational mitigation, not a structural one. Until a second
   principal is hired (Phase 2), the operator's compromise is
   un-segregated.
6. **Edge rate limiting only at application layer.** Cloudflare's
   coarse rate limit + per-IP Bucket4j on the backend, not a dedicated
   abuse-control system. Phase 1.11 adds Redis-backed distributed
   limiter and explicit Cloudflare WAF rules.
7. **No formal pen-test yet.** Phase 1.21 commits to one external
   pen-test before SOC 2 Type II audit.
8. **Verifier WASM not yet shipped.** Today `/verify` is server-side;
   the WASM-in-browser verifier (Phase 1.20) is the real
   zero-trust-on-EATF story. Until then, the server-side verifier
   remains a potential DoS target.

---

## 7. Plan-linked TODOs

Every `planned` or `partial` row in section 4 cites a phase. The phases
correspond to the EATF roadmap (`PLAN.md` and the auditor-auto-brain
plan that produced Phase 0). Summary:

| Phase | Step | Closes |
|---|---|---|
| Phase 1.2 | ETSI EN 319 401 self-assessment | Document gap-analysis cross-references |
| Phase 1.4 | Termination plan | 4.3.2 (public key mirror), 5.4 (insider risk) |
| Phase 1.5 | AEP-profile-v1.md | 4.3.5 (schema contract) |
| Phase 1.6 | Endpoint allowlist | 4.2.6 (signing oracle abuse) |
| Phase 1.7 | Two-person production rule | 5.4 (insider risk) |
| Phase 1.9 | Managed HSM (PKCS#11) | 4.2.4 (filesystem keys), residual #1 |
| Phase 1.10 | Key rotation API + ledger key-versioning | 4.2.3 (algo agility), 5.2 (rotation), residual #2 |
| Phase 1.11 | Redis-backed rate limiter | 4.4.3 (multi-node), 4.9.1 (DoS), residual #6 |
| Phase 1.12 | Reproducible verifier build | 4.3.4, 4.7.1 (supply chain) |
| Phase 1.13 | SBOM + digest-pinned images | 4.7.1, 4.7.3 (supply chain) |
| Phase 1.14 | SOC 2 Type I kickoff | Residual #4 |
| Phase 1.15 | Audit log archival + Prometheus | 4.9.4 (disk), observability |
| Phase 1.17 | Per-request short-lived BFF JWT | 4.1.4 (BFF mint key) |
| Phase 1.18 | Public ledger roll-up viewer | 4.4.5 (truncation detection), 5.4 (insider) |
| Phase 1.19 | CSP + XSS hardening | 4.7.2, 4.8.5 (frontend) |
| Phase 1.20 | WASM in-browser verifier | 4.3.3 (server DoS), residual #8 |
| Phase 1.21 | External penetration test | Residual #7 |
| Phase 1.24 | Qualified TSP partner | 4.2.5, 4.6.2 (qualified TSA) |
| Phase 1.27 | TSA fallback chain + async queue | 4.6.1 (single TSA), 4.9.3 (blocking call), residual #3 |
| Phase 2.14 | SOC 2 Type II | Residual #4 |
| Phase 2.15 | ISO 27001 | Residual #4 |

---

## Document control

| Field | Value |
|---|---|
| Version | 1.0-draft |
| Date | 2026-05-12 |
| Status | Comment period open |
| Next review | After Phase 1.9 (HSM landing) or 2026-08-12, whichever first |
| Owner | Senior Architect (currently founder) |
| Disclosure contact | `security@aletheia.ai` (see `SECURITY.md`) |

This document will be updated **non-silently**: every revision is
committed to git with a signed tag; the changelog at the head of the
file records what changed and why. An auditor reviewing a specific
revision should reference the git tag, not the file alone.




