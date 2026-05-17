"""RFC 3161 timestamp parsing + verification.

Mirrors lib/src/tsa.ts. The TS reference uses pkijs; the Python
port uses asn1crypto for the TimeStampToken / CMS structure and
pyca/cryptography for the SignerInfo signature verification.

This is "structural-check + SignerInfo signature only" parity
with the TS reference. Chain-to-root validation against pinned
TSA roots is documented as planned in lib-python/README.md.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass

from asn1crypto import cms, tsp
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509 import load_der_x509_certificate


@dataclass
class TsaCheck:
    tsa_present: bool
    raw_size_bytes: int
    gen_time: str | None  # ISO 8601 string, or None
    message_imprint_matches: bool | None  # None when we can't determine
    signature_verified: bool | None  # None when no embedded cert
    signer_subject: str | None
    signer_issuer: str | None


def inspect_tsa(tsr_b64: str, expected_hash_hex: str) -> TsaCheck:
    """Parse and structurally verify an RFC 3161 token.

    `tsr_b64` is the contents of timestamp.tsr (base64) — the
    verifier strips ASCII whitespace and decodes. `expected_hash_hex`
    is the hex SHA-256 the verifier expects to find as the message
    imprint.
    """
    try:
        raw = base64.b64decode(tsr_b64.strip(), validate=False)
    except Exception:
        return _empty()

    if not raw:
        return _empty()

    # An RFC 3161 response can be either:
    #   1. A bare TimeStampResp (with status + timeStampToken)
    #   2. A bare TimeStampToken (CMS SignedData)
    # We accept both shapes.
    token_bytes = _extract_token(raw)
    if token_bytes is None:
        return _empty()

    try:
        signed = cms.ContentInfo.load(token_bytes)
        if signed["content_type"].native != "signed_data":
            return _empty()
        sd = signed["content"]
    except Exception:
        return _empty()

    try:
        tst_info_bytes = sd["encap_content_info"]["content"].native
        tst_info = tsp.TSTInfo.load(tst_info_bytes)
        imprint = tst_info["message_imprint"]["hashed_message"].native
        imprint_hex = imprint.hex()
        message_imprint_matches = imprint_hex == expected_hash_hex.lower()
        gen_time = tst_info["gen_time"].native.isoformat() if tst_info["gen_time"].native else None
    except Exception:
        message_imprint_matches = None
        gen_time = None

    signer_subject = None
    signer_issuer = None
    signature_verified: bool | None = None

    try:
        certs = sd["certificates"]
        if certs:
            cert_der = certs[0].chosen.dump()
            cert = load_der_x509_certificate(cert_der)
            signer_subject = cert.subject.rfc4514_string()
            signer_issuer = cert.issuer.rfc4514_string()

            # Verify the first SignerInfo against this cert.
            signer_info = sd["signer_infos"][0]
            signature = signer_info["signature"].native

            # Compute the signed-attributes DER (or fall back to
            # encap_content_info content).
            if signer_info["signed_attrs"]:
                signed_attrs = signer_info["signed_attrs"]
                signed_attrs_der = signed_attrs.dump(force=True)
                # CMS requires the signed-attributes to be re-encoded
                # with the SET OF tag (0x31), not the implicit [0]
                # context-specific tag they're carried with on the wire.
                signed_attrs_der = b"\x31" + signed_attrs_der[1:]
                tbs = signed_attrs_der
            else:
                tbs = tst_info_bytes

            pubkey = cert.public_key()
            if isinstance(pubkey, rsa.RSAPublicKey):
                try:
                    pubkey.verify(signature, tbs, padding.PKCS1v15(), hashes.SHA256())
                    signature_verified = True
                except InvalidSignature:
                    signature_verified = False
            else:
                # ECDSA TSA signing is rare in v0.1 deployments;
                # treat as inconclusive for now (verifier ignores
                # signature_verified=None).
                signature_verified = None
    except Exception:
        # Parsing failure → leave signature_verified at None
        pass

    return TsaCheck(
        tsa_present=True,
        raw_size_bytes=len(raw),
        gen_time=gen_time,
        message_imprint_matches=message_imprint_matches,
        signature_verified=signature_verified,
        signer_subject=signer_subject,
        signer_issuer=signer_issuer,
    )


def _extract_token(raw: bytes) -> bytes | None:
    """Try parse as TimeStampResp first; fall back to bare token."""
    try:
        resp = tsp.TimeStampResp.load(raw)
        # Status must be 0 (granted) or 1 (granted with mods)
        status = resp["status"]["status"].native
        if status not in ("granted", "granted_with_mods"):
            return None
        if resp["time_stamp_token"]:
            return resp["time_stamp_token"].dump()
    except Exception:
        pass

    # Try as bare CMS ContentInfo
    try:
        cms.ContentInfo.load(raw)
        return raw
    except Exception:
        return None


def _empty() -> TsaCheck:
    return TsaCheck(
        tsa_present=False,
        raw_size_bytes=0,
        gen_time=None,
        message_imprint_matches=None,
        signature_verified=None,
        signer_subject=None,
        signer_issuer=None,
    )
