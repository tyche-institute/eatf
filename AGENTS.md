# AGENTS.md — guidance for AI agents working in this repository

This file is read by AI coding assistants (Claude Code, Cursor,
Aider, etc.) when they first open this repository. It tells them
what EATF is, what's in scope, what's out of scope, and how to
make changes the maintainers will accept.

Human contributors are also welcome to read it, but the canonical
human-facing docs are [`README.md`](./README.md),
[`CONTRIBUTING.md`](./CONTRIBUTING.md),
[`ROADMAP.md`](./ROADMAP.md), and the pages under
[`docs/`](./docs/).

---

## 1. What this repository is

EATF (Agent Trust Framework) is an open specification and
TypeScript reference implementation for cryptographically
verifiable AI agent self-attestation. The artefact is a small
ZIP file format — Agent Evidence Package (`.aep`) — that bundles:

- A canonical payload (`canonical.bin`).
- A SHA-256 of that canonical form (`hash.sha256`).
- A classical signature (`signature.sig`, RSASSA-PKCS1-v1_5 + SHA-256).
- Optionally a post-quantum signature (`signature_pqc.sig`, ML-DSA-65).
- An RFC 3161 timestamp (`timestamp.tsr`).
- An OVERT 1.0 receipt (`overt_receipt.json`).
- Attestation metadata (`metadata.json`).
- The issuer's public key (`public_key.pem`).

Verification is **offline**: a relying party with only the file
and a trust anchor can assert authenticity, integrity, and
timeliness without contacting any third party.

Wire format: [`docs/aep-profile.md`](./docs/aep-profile.md).
Verifier orchestration: [`lib/src/verifier.ts`](./lib/src/verifier.ts).
Signer: [`lib/src/signer.ts`](./lib/src/signer.ts).

## 2. Positioning — what EATF deliberately is NOT

These are **non-negotiable** statements; any change that weakens
them will be rejected. They appear verbatim in
[`NOTICE`](./NOTICE), [`README.md`](./README.md),
[`CONTRIBUTING.md`](./CONTRIBUTING.md), and
[`docs/aep-profile.md`](./docs/aep-profile.md).

- **EATF is NOT an eIDAS trust service** under Regulation (EU)
  910/2014 Article 3(16). It does not issue qualified
  certificates, signatures, timestamps, or attestations, and is
  not a Qualified Trust Service Provider.
- **EATF agent attestations are NOT QEAA** (Qualified Electronic
  Attestations of Attributes) under eIDAS Article 3(45). They are
  technical self-attestations.
- **EATF is NOT a managed service.** No hosted backend, no agent
  registry, no marketplace, no compliance dashboard, no paid
  tiers. The project is a library + spec; service infrastructure
  is out of scope by design (see
  [`CONTRIBUTING.md`](./CONTRIBUTING.md) "What we will and will
  not accept").
- **EATF is NOT a safety or alignment claim.** The framework
  attests "this output came from this agent at this time"; it
  does not assert that the output is correct, helpful, safe,
  unbiased, or appropriate.

Any contribution that implies qualified status, builds in a
hosted registry / marketplace, or claims AI-safety semantics will
be declined.

## 3. Repository layout

```
lib/                — @eatf/verifier package: TypeScript verifier + signer.
cli/eatf-verify/   — Offline verifier CLI.
cli/eatf-sign/     — Offline signer CLI.
cli/eatf-inspect/  — Structural dump of an .aep (does NOT verify).
test-vectors/      — Conformance vectors (4 valid + 1 invalid).
test-vectors/keys/ — Public-and-private dev RSA keypair (see its README).
schemas/           — JSON Schema 2020-12 for the AEP metadata.json.
docs/              — Specifications and design notes.
.github/workflows/ — CI: schema-validate, verifier-test, conformance, roundtrip, hygiene, DCO.
ROADMAP.md         — What's next + what's deliberately out of scope.
CHANGELOG.md       — Per-release contents.
```

## 4. How to verify the project works

```bash
git clone https://github.com/tyche-institute/eatf
cd eatf
(cd lib && npm install && npm run build)
(cd cli/eatf-verify && npm install)
(cd cli/eatf-sign && npm install)

# Conformance against the bundled test vectors.
node cli/eatf-verify/bin/eatf-verify.js --conformance test-vectors/
# Expected: 4 verified, 1 rejected, 0 contract mismatches.

# Sign-then-verify round-trip.
echo "Hello, world." > /tmp/payload.txt
cat > /tmp/meta.json <<'JSON'
{
  "schema": "urn:eatf:spec:aep:metadata:1.0",
  "attestation_id": "att_demo_01",
  "created_at": "2026-05-15T00:00:00Z",
  "agent_id": "urn:eatf:tenant:demo:agent:hello",
  "action_type": "demo.hello-world",
  "policy_id": "atap-basic",
  "policy_version": "1.0",
  "policy_coverage": 1.0,
  "policy_decision": "allow",
  "format_version": "ATAP-1.0"
}
JSON
node cli/eatf-sign/bin/eatf-sign.js \
  --payload /tmp/payload.txt \
  --key test-vectors/keys/dev-rsa-4096.key \
  --public-key test-vectors/keys/dev-rsa-4096.pem \
  --metadata /tmp/meta.json \
  --scope foundational:aep-response \
  --timestamp test-vectors/valid/valid-overt-profile/package.aep:timestamp.tsr \
  --out /tmp/hello.aep

node cli/eatf-verify/bin/eatf-verify.js /tmp/hello.aep
# Expected: verify=true.
```

CI runs these same checks on every push to `main` (plus DCO
sign-off verification on every pull request).

## 5. Contribution conventions

- **Apache License 2.0.** All contributions are accepted under
  Apache 2.0.
- **DCO sign-off** on every commit (`git commit -s`). No CLA.
  Mechanism documented in [`CONTRIBUTING.md`](./CONTRIBUTING.md).
- **Pull requests required for `main`.** Branch protection
  enforces 5 status checks (schema-validate, verifier-test,
  conformance, roundtrip, hygiene). Required linear history; no
  force pushes; no deletion.
- **`docs/` changes are first-class.** Spec and design-rationale
  updates are reviewed with the same care as code.
- **AEP wire-format changes are versioned.** A backwards-
  incompatible change to the format bumps the profile URN
  (`urn:eatf:spec:aep:1.0` → `urn:eatf:spec:aep:2.0`) and gets a
  separate spec document.

## 6. What we will and will not accept

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full list. The
short version:

**We welcome:**

- Bug fixes; additional conformance test vectors; additional
  failure-mode vectors; documentation improvements; translations.
- New language bindings for the verifier (Python, Go, Rust) — see
  [`ROADMAP.md`](./ROADMAP.md) §v0.2 and §v0.3 for stack
  recommendations.
- Independent verifier implementations + conformance reports
  against the published test vectors.
- Adapter helpers for popular agent frameworks (LangChain,
  CrewAI, AutoGen, Google ADK, OpenAI Agents) IF they remain
  thin wrappers over the public spec, with no hidden network
  dependency on any operator's hosted service.

**We will likely decline:**

- Changes that turn the reference implementation into a managed
  service (multi-tenant SaaS, customer onboarding, billing
  primitives, ops dashboards). EATF is a library + spec; service
  infrastructure is out of scope by design.
- Changes that imply qualified-trust-service status under eIDAS.
  Article 3(16) and 3(45) positioning is load-bearing.
- Vendor-locked integrations baked into the reference
  implementation. Generic adapter interfaces are preferred so
  users can plug in their own vendor.
- Anything that claims AI safety, alignment, or "trustworthiness"
  in a substantive sense — the framework attests, it does not
  judge.

## 7. Useful AI-agent prompts

### 7.1 Verify the project builds and passes conformance

> Read AGENTS.md and ROADMAP.md.
> Run a full health check:
>   - `git log --oneline -5`
>   - `gh run list --repo tyche-institute/eatf --limit 5`
>   - `(cd lib && npm install && npm run build && npx vitest run)`
>   - `(cd cli/eatf-verify && npm install)`
>   - `(cd cli/eatf-sign && npm install)`
>   - `node cli/eatf-verify/bin/eatf-verify.js --conformance test-vectors/`
> Report: CI status, vitest pass count, conformance summary.

### 7.2 Add a new failure-mode test vector

> Read AGENTS.md and `docs/aep-profile.md`.
> Add a new vector under `test-vectors/invalid/<descriptive-name>/`.
> Use the bundled signer (`cli/eatf-sign`) to build a valid
> `.aep`, then mutate the package to introduce the specific
> failure mode (e.g. flip a byte in `canonical.bin` for
> tampered-manifest, swap `signature.sig` for an empty file for
> bad-signature-classical). Write `verify-expected.txt` with the
> expected diagnostic, and a `README.md` describing what the
> vector exercises. Verify with `eatf-verify --conformance
> test-vectors/` and confirm 0 contract mismatches. Commit with
> DCO sign-off; open PR.

### 7.3 Port the verifier to a new language

> Read AGENTS.md and ROADMAP.md (v0.2.0 / v0.3.0 sections).
> Implement a fresh verifier in <language>. The conformance
> contract is `test-vectors/`: produce the same `verify=true /
> false` outcomes that the TypeScript reference produces on every
> vector. Place the new implementation under `lib-<language>/`
> with its own README, package metadata, and CI job. Do NOT port
> the existing internal SDK clients (they are managed-service
> clients, out of scope here).

### 7.4 Audit a PR for scope creep

> Read AGENTS.md §2, §3, §6.
> Then review the PR diff and report whether it:
>   - Introduces any managed-service surface (hosted endpoints,
>     API keys, tenant management, billing).
>   - Weakens the "not an eIDAS trust service" positioning.
>   - Implies AI safety / alignment claims.
>   - Pulls in named third-party dependencies in a vendor-locking
>     way.
> If any of these are present, recommend declining the PR with
> a polite explanation pointing at CONTRIBUTING.md "What we will
> not accept".

## 8. Cross-references

- The public-key history mirror for production deployments:
  <https://github.com/tyche-institute/eatf-trust-anchors>.
- The maintaining organisation:
  <https://github.com/tyche-institute>.
- Project home page:
  <https://github.com/tyche-institute/eatf>.

There is no project marketing site, no Discord, no Slack. Issues
and pull requests on this repository are the only sanctioned
communication channels. Security disclosures follow
[`SECURITY.md`](./SECURITY.md).
