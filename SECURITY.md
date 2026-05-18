# Security Policy

## 🔒 Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### Private Disclosure

If you discover a security vulnerability in the Aletheia AI Enterprise Agent Trust Framework, please report it privately:

**Email:** security@eatf.eu (preferred) or security@aletheia.ai (legacy alias)
**PGP Key:** Published at `https://eatf.eu/.well-known/pgp.asc` (fingerprint also in `/.well-known/security.txt`); ask via the email above if you need a different channel.
**security.txt:** [`https://eatf.eu/.well-known/security.txt`](https://eatf.eu/.well-known/security.txt) (also at `frontend/public/.well-known/security.txt`).
**Full policy:** [`docs/legal/disclosure-policy.md`](docs/legal/disclosure-policy.md).

### What to Include

Please include as much of the following information as possible:

- **Type of vulnerability** (e.g., crypto weakness, auth bypass, injection)
- **Full path** of the source file(s) related to the vulnerability
- **Location** of the affected source code (tag/branch/commit or direct URL)
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept or exploit code** (if possible)
- **Impact** of the issue (what an attacker could do)
- **Suggested fix** (if you have one)

### Response Timeline (SLA)

Phase 1 step 1.8: these are commitments, not aspirations. Misses are themselves a security event and will be disclosed publicly in the next quarterly transparency note.

- **Acknowledgment of receipt:** within **72 hours** (best effort within 24h on business days).
- **Initial severity assessment:** within **7 days**.
- **Coordinated disclosure deadline:** **90 days** from acknowledgment, extendable by mutual agreement when a fix is in-flight.
- **Public disclosure:** after a fix is deployed and verified, with a security advisory on GitHub and a CVE if applicable.
- **Bug bounty:** not active yet — see Phase 2.x in the roadmap. We will, however, publicly credit researchers who follow this policy.

---

## 🛡️ Security Measures

EATF should be read here as an **early-stage, pilot-oriented trust platform**
with explicit demo and research surfaces. This document describes the current
security posture of the codebase and deployment paths; it is **not** a claim
of certification, HSM-backed production readiness, or complete operational
hardening across every surface in the repository.

### Cryptographic Integrity

EATF uses **post-quantum cryptography** (ML-DSA) alongside RSA for long-term signature verification:

- **Audit trail:** Hash-chained events with dual signatures (PQC + RSA)
- **Evidence packages:** Cryptographically signed `.aep` files
- **Delegation chains:** Signature verification at each level
- **Timestamps:** RFC 3161 timestamping (QTSP integration)

### Key Management

- **PQC keys:** Configurable via `AI_ALETHEIA_PQC_KEY_PATH`; local and demo setups may use filesystem-backed keys
- **HSM support:** Planned for production (QTSP-ready)
- **Key rotation:** Not yet automated (manual process documented)
- **Environment secrets:** Never committed to Git (`.gitignore` enforced)

### Authentication & Authorization

- **OAuth2/OIDC:** Google OAuth for user authentication
- **NextAuth.js:** Session management
- **Multi-tenancy:** Organization-based isolation
- **RBAC:** Role-based access control centered on tenant-scoped operations

### API Security

- **JWT tokens:** Signed with `AI_ALETHEIA_JWT_SECRET`
- **BFF mint key:** `AI_ALETHEIA_BFF_MINT_KEY` (same value on Next.js server and backend) protects `GET /api/auth/session/bff` used by the Next proxy to mint API JWTs by `userId`. Treat like a shared service secret; use a strong random value in production (`docs/developers/en/bff-api-jwt-mint.md`).
- **Authenticated API:** Most `/api/**` routes require `Authorization: Bearer <JWT>` (see `SecurityConfig`). Exceptions: `/api/auth/**`, `/api/public/**` (e.g. invite signup when configured).
- **OAuth provisioning:** `AI_ALETHEIA_OAUTH_AUTO_PROVISION` — when `false`, OAuth does not create new users (existing accounts only).
- **Invite signup:** `AI_ALETHEIA_INVITE_SECRET` — when set, enables `POST /api/public/register-invite` / `/auth/register` for VIEWER accounts in the default tenant.
- **Rate limiting:** Per-IP token bucket on `/api/**` (Bucket4j), configurable via `ai.aletheia.ratelimit.*` (disabled in `application-test.properties`)
- **CORS:** Configured for frontend/backend separation
- **Input validation:** Spring Boot validators + custom checks

### Database Security

- **PostgreSQL:** Production database (not SQLite)
- **Connection encryption:** SSL/TLS recommended
- **Parameterized queries:** JPA/Hibernate (SQL injection protection)
- **Multi-tenancy isolation:** Row-level security via organization_id

### Infrastructure

- **Canonical public architecture:** Cloudflare-hosted frontend plus Hetzner-hosted backend (see `docs/cloudflare-architecture.md`)
- **Legacy/secondary ops paths:** Ansible, manual runbooks, and local Docker remain available for development or recovery, but they are not the primary public production contract
- **Environment variables:** Secrets managed via env files or deployment automation, depending on the path
- **Docker:** Supported for local/containerized workflows; not the canonical public deployment story

---

## 🚨 Known Issues & Mitigations

### Current Limitations

1. **PQC key rotation:** Not automated (manual process required)
2. **Rate limiting:** Implemented at the application layer for `/api/**`, but not yet backed by a broader edge/gateway abuse-control program
3. **HSM integration:** Not yet available (keys stored on filesystem)
4. **Audit log pruning:** No automated archival (disk can fill up)
5. **Multi-region:** Not supported (single deployment only)

### Recommended Mitigations (Production)

- [ ] Add edge/gateway rate limiting and abuse controls beyond the current application-layer limiter
- [ ] Integrate HSM for PQC key storage
- [ ] Set up automated audit log archival (S3, cold storage)
- [ ] Enable PostgreSQL connection encryption
- [ ] Configure firewall rules (only allow frontend → backend, backend → DB)
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Regular security audits and penetration testing

---

## 🔐 Security Best Practices (For Developers)

### Never Commit Secrets

**Forbidden in Git:**
- API keys (OpenAI, Google OAuth, etc.)
- JWT secrets
- Database passwords
- PQC private keys
- `.env` files with real credentials

**Use `.gitignore` and environment variables.**

### Code Review Requirements

**Security-critical changes require review:**
- Cryptographic operations (`/backend/src/main/java/ai/aletheia/crypto/`)
- Authentication/authorization logic
- Database migrations
- Deployment scripts
- API endpoints handling sensitive data

**See `CODEOWNERS` for required reviewers.**

### Dependency Security

- **Dependabot:** Enabled for automatic vulnerability alerts
- **Regular updates:** Check for CVEs in Maven/npm dependencies
- **Lock files:** Use `package-lock.json` and `pom.xml` checksums

### Testing Security

- **No real keys in tests:** Use mocked keys or test fixtures
- **No production data:** Use synthetic data only
- **Clean up:** Delete test evidence packages after tests

---

## 🏛️ Compliance & Standards

EATF is designed as an implementation and evidence layer relevant to:

- **EU AI Act** (High-risk AI systems)
- **GDPR** (Data privacy)
- **ISO 27001** (Information security)
- **SOC 2** (Service organization controls)
- **QTSP standards** (Qualified Trust Service Providers)

See `docs/legal/` for compliance documentation.

---

## 📚 Security Documentation

- **Architecture:** [docs/diagrams/architecture.md](docs/diagrams/architecture.md)
- **Crypto reference:** [docs/developers/en/crypto-reference.md](docs/developers/en/crypto-reference.md)
- **Trust model:** [docs/users/en/trust-model.md](docs/users/en/trust-model.md)
- **Deployment:** [deploy/README.md](deploy/README.md)

---

## 🙏 Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers who help improve EATF security.

---

**Last updated:** 2026-05-12 (Phase 1 step 1.8 — formalized disclosure SLAs, added security.txt + disclosure-policy.md references, updated contact to security@eatf.eu).
**Contact:** security@eatf.eu (legacy alias: security@aletheia.ai)
