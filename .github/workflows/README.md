# .github/workflows/

Planned CI workflows for v0.1:

| Workflow file        | Purpose                                                                          |
|----------------------|----------------------------------------------------------------------------------|
| `dco.yml`            | Verify every commit in a PR carries a `Signed-off-by:` trailer (DCO).            |
| `lint.yml`           | Lint Markdown, JSON, and TypeScript / Java source.                               |
| `schema-validate.yml`| Validate `../schemas/*.schema.json` and validate test vectors against schemas.   |
| `conformance.yml`    | Run the reference verifier against `../test-vectors/`.                           |
| `unit.yml`           | Run unit tests for `../lib/` and `../cli/`.                                      |

## v0.1.0 status

Stub. Workflows land alongside the runnable implementation in
successive 0.1.x point releases.
