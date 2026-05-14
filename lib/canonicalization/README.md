# lib/canonicalization

Canonicalisation primitives used across the EATF stack.

## Scope

- **JSON:** RFC 8785 JSON Canonicalization Scheme (JCS). Every JSON
  document signed by EATF is canonicalised to JCS bytes before
  hashing.
- **ZIP:** deterministic AEP envelope construction. Files are written
  in sorted path order; per-entry timestamps are fixed to the AEP
  protocol epoch; compression mode is `STORED`; central-directory
  ordering matches local-file-header ordering.

## v0.1.0 status

Stub. Reference implementation lands in a 0.1.x point release.

## Reference

- [RFC 8785 — JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)
- [APPNOTE.TXT — .ZIP File Format Specification](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)
