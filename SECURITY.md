# Security Policy

## Supported versions

EATF is currently in a v0.x research-preview phase. Only the most
recent published tag receives security updates. Once the project
reaches v1.0, this section will be expanded with a formal support
window.

| Version | Supported |
|---------|-----------|
| 0.1.x   | yes (current) |
| < 0.1   | no        |

## Reporting a vulnerability

**Do not open a public issue, pull request, or discussion thread for
security vulnerabilities.** Public disclosure before a fix is
available can expose downstream operators to risk.

Please report security issues by email to
**security@tyche.institute**. PGP encryption is preferred but not
required; the project PGP key fingerprint and a link to its public
key will be published in this file once the project's key
infrastructure is in place. Until then, plain-text email is
acceptable.

Include in your report:

1. A description of the vulnerability and its potential impact.
2. Steps to reproduce, with a minimal proof-of-concept if possible.
3. The version (tag or commit hash) of EATF that you tested against.
4. Any suggested mitigations or fixes.
5. Whether you intend to publish your own write-up, and on what
   timeline.

You should receive an acknowledgement within **72 hours** and a
substantive triage response (severity assessment, planned fix
timeline) within **10 working days**. If you do not, please follow up
on the same thread.

**No bug bounty.** EATF does not offer monetary rewards for
vulnerability reports. We will credit reporters publicly with their
consent (see "Hall of fame" below) and we treat coordinated disclosure
as a contribution worth acknowledging, but we cannot offer cash. If
that affects your decision to report, we still encourage you to
report.

**CVE assignment.** Where a vulnerability has impact beyond this
project (for example, in an upstream library), we will request a CVE
ID via MITRE's CVE Numbering Authority program and credit the
reporter on the resulting advisory.

## Disclosure policy

We follow a coordinated disclosure model:

1. Reporter contacts security@tyche.institute privately.
2. Maintainers triage and confirm the vulnerability.
3. A fix is developed in a private branch.
4. A coordinated release date is agreed with the reporter, typically
   **90 days** from initial report, shorter if the issue is being
   actively exploited.
5. On the release date: the fix is published, an advisory is issued,
   and the reporter is credited (with their consent).

We will not pursue legal action against researchers who:

- Make a good-faith effort to avoid privacy violations, destruction
  of data, or interruption or degradation of services.
- Only interact with accounts or systems they own or have explicit
  permission to test.
- Disclose responsibly and give us reasonable time to fix issues
  before public disclosure.

## Scope

In scope:

- The EATF reference implementation in this repository (`lib/`,
  `cli/`, `schemas/`, `examples/`).
- The AEP wire-format specification in `docs/aep-profile.md`.
- The conformance test vectors in `test-vectors/`.

Out of scope:

- Third-party reference deployments operating EATF (h2oatlas.ee,
  matx.ee, eaudit.ee, and similar). Report deployment-specific
  issues to the deployment operator directly.
- Issues in upstream dependencies (Bouncy Castle, jose, etc.). Those
  should be reported to the upstream project; we will track upstream
  advisories and ship updated pins as needed.
- Denial-of-service issues that require an unrealistic resource
  envelope (e.g. multi-gigabyte input files); please open a normal
  performance-issue ticket instead.

## Trust anchors and key compromise

If a private signing key used by a reference deployment is suspected
to be compromised, contact the deployment operator immediately and CC
security@tyche.institute. The EATF threat model assumes that operators
maintain their own key custody; key-management compromise on an
operator side is a deployment incident, not an EATF library
vulnerability, but we will help coordinate disclosure if the same
class of issue could affect other operators.

## Hall of fame

Researchers who report valid vulnerabilities and consent to public
acknowledgement will be listed in `docs/security-acknowledgements.md`
(file added once the first valid report is received).
