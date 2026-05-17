# .github/workflows/

| Workflow file           | Trigger             | Purpose                                                                                  |
|-------------------------|---------------------|------------------------------------------------------------------------------------------|
| `ci.yml`                | push, pull_request  | DCO sign-off, schema validation, TS verifier unit tests, conformance, round-trip, Python verifier matrix, hygiene. |
| `publish-python.yml`    | tag `v*`, manual    | Build and publish `lib-python/` to PyPI as `eatf-verifier` via OIDC trusted publisher.   |

## PyPI publish — one-time setup

The `publish-python.yml` workflow uses **PyPI Trusted Publishing**
(OpenID Connect). No API token is stored in this repo. The PyPI
side must be configured with a Trusted Publisher entry pointing at
this workflow.

Steps for the PyPI account owner:

1. Register the `eatf-verifier` project name on PyPI. Either:
   - Upload a first build manually with `twine upload` using an
     API token, then delete the token; or
   - Use PyPI's "Pending Publisher" flow under the project's
     Publishing settings, which reserves the name before the
     first OIDC publish.
2. In the project's PyPI "Publishing" settings, add a Trusted
   Publisher entry:
   - Repository owner:  `tyche-institute`
   - Repository name:   `eatf`
   - Workflow filename: `publish-python.yml`
   - Environment name:  `pypi`
3. In this repo's *Settings → Environments*, create an environment
   named `pypi`. Optionally restrict it to protected tags (`v*`).

After this, any pushed `v*` tag will build + publish automatically.
The workflow uses `skip-existing: true` so re-tagging an already-
published version is a no-op rather than a hard failure.
