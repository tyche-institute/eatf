# lib/timestamping

RFC 3161 Time-Stamp Protocol client used to bind the manifest
signature to a trusted wall-clock time.

## Behaviour

1. Compute `H(manifest.sig.cms)` with the AEP profile's hash algorithm
   (default SHA-256).
2. Build an RFC 3161 `TimeStampReq` with the hash and a 32-byte
   nonce.
3. Submit the request to the configured TSA endpoint (HTTP or HTTPS).
4. Receive a `TimeStampResp` and validate the status code, the TSA
   certificate chain (RFC 5280), and that the response's `messageImprint`
   matches the request hash.
5. Persist the response bytes verbatim as `timestamps/manifest.tsr` in
   the AEP package.

The signer is responsible for invoking this module after producing
the manifest signature. Verifiers replay step 5's validation against
their configured TSA trust anchors.

## v0.1.0 status

Stub. Reference implementation lands in a 0.1.x point release.

## Reference

- [RFC 3161 — Internet X.509 Public Key Infrastructure Time-Stamp Protocol (TSP)](https://www.rfc-editor.org/rfc/rfc3161.html)
