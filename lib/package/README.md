# lib/package

AEP ZIP envelope construction and parsing.

## Responsibilities

- Build the deterministic ZIP layout documented in
  [`../../docs/aep-profile.md`](../../docs/aep-profile.md).
- Compute content-addressed digests for every record file and
  populate the manifest's `records[].digest` field.
- Embed the agent attestation (`attestations/agent.vc.json`) when
  provided by the caller.
- Emit the final byte stream that the signer and timestamping client
  operate on.

The package module is intentionally agnostic to the *meaning* of the
records it carries. Record-format profiles (e.g. the OVERT
observation record schema) are defined in `../../schemas/` and
validated separately.

## v0.1.0 status

Stub. Reference implementation lands in a 0.1.x point release.
