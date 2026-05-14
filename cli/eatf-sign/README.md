# eatf-sign

```
eatf-sign --in <records-dir> --key <pem> [--cert <pem>] \
          [--mldsa-key <pem>] [--tsa <url>] --out <pkg.aep>
```

Builds an AEP from a directory of action records, signs the manifest
with the configured classical key, signs again with the post-quantum
key if provided, and stamps the manifest signature via the configured
RFC 3161 TSA.

## v0.1.0 status

Stub. CLI lands in a 0.1.x point release.
