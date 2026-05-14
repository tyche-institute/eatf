# Contributing to EATF

Thank you for considering a contribution. EATF is maintained by Tyche
Institute (Estonian non-profit, registration in progress) under the
Apache License 2.0 and is open for review, patches, and discussion.

## Developer Certificate of Origin

This project uses the **Developer Certificate of Origin (DCO)**
instead of a Contributor License Agreement. Every commit must carry
a `Signed-off-by:` trailer attesting to the DCO.

Sign off each commit with the `-s` flag:

```sh
git commit -s -m "Your change description"
```

This appends a line such as:

```
Signed-off-by: Your Name <your.email@example.com>
```

By signing off, you certify the following (verbatim from
<https://developercertificate.org/>):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Pull requests with unsigned commits will be asked to amend (a CI
check enforces this automatically).

## Why DCO and not CLA?

Apache 2.0 already grants this project broad rights including a
patent grant. A Contributor License Agreement adds marginal legal
protection at significant overhead — legal review, signature
collection, friction for casual contributors. The Linux kernel,
Kubernetes, Docker, GitLab, and many other large projects use the
DCO. We follow that convention.

## Code of Conduct

Participation is governed by [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md).

## Workflow

1. Open an issue describing the change you have in mind, especially
   for anything touching the AEP wire format, signer/verifier
   semantics, or the schemas. Discussion before code saves time.
2. Fork, branch, commit with DCO sign-off, push, open a pull
   request.
3. CI runs lint, type-check, unit tests, schema validation, and
   verifier conformance against the published test vectors. All
   green is required before review.
4. A maintainer reviews and either merges or requests changes.

## Style

- Source files carry the standard Apache 2.0 short license header.
- Schemas are JSON Schema 2020-12.
- AEP profile changes are versioned. Backwards-incompatible changes
  bump the major version of the AEP profile URN
  (`urn:eatf:spec:aep:1.0` → `urn:eatf:spec:aep:2.0`).

## Security disclosures

Do **not** open a public issue for vulnerability reports. Follow
[SECURITY.md](./SECURITY.md).

## What we will and will not accept

We welcome:

- Bug fixes, additional test vectors, additional examples.
- Documentation improvements, glossary entries, translations.
- New language bindings (Python, Go, Rust verifier ports).
- Conformance reports against the published test vectors.

We will likely decline (politely, with explanation):

- Changes that would turn the reference implementation into a
  managed service (multi-tenant SaaS, customer onboarding, billing
  primitives, ops dashboards). EATF is a library + spec; service
  infrastructure is out of scope by design.
- Changes that would imply EATF operates as an eIDAS trust service
  or issues QEAA — those would contradict the project's stated
  legal positioning.
- Vendor-locked integrations baked into the reference
  implementation. Generic adapter interfaces are preferred so users
  can plug in their own vendor.

If you are unsure where a proposed change falls, open an issue
first.
