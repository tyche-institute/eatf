"""Tests for aletheia.evidence.EvidenceAPI.verify — offline .aep verification.

Mirrors test/lib.test.js in @eatf/cli. We synthesise bundles at runtime so
the tests don't depend on a live signing key, and we replicate the
backend's exact non-standard 49-byte DigestInfo so the production code
path is exercised (not a happy-path-only mock).
"""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import pytest

cryptography = pytest.importorskip("cryptography")
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from aletheia.evidence import (
    EVIDENCE_BUNDLE_FILES,
    EvidenceAPI,
    EvidenceVerifyResult,
)


# Backend's hand-rolled SHA-256 DigestInfo prefix (without the standard
# `05 00` NULL parameters). 17 bytes; followed by the 32 hash bytes for
# a total of 49 bytes vs the standard 51-byte form.
_DIGEST_INFO_PREFIX = bytes.fromhex("302f300b0609608648016503040201" + "0420")


def _build_bundle(*, response: bytes = b"test response\n", composite: bool = True) -> tuple[bytes, rsa.RSAPrivateKey, bytes]:
    """Produce a self-consistent bundle. Returns (zip_bytes, priv_key, hash_bytes)."""
    import hashlib

    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub_pem = priv.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    canonical = (
        response
        + b'\n{"claim":"","confidence":0.000000,"model":"external","policy_version":"1.0"}'
        if composite
        else response
    )
    h = hashlib.sha256(response).digest()
    h_hex = h.hex().encode("utf-8")

    digest_info = _DIGEST_INFO_PREFIX + h
    # PKCS#1 v1.5 manual signing matching the Java backend's NONEwithRSA path.
    n = priv.private_numbers().public_numbers.n
    d = priv.private_numbers().d
    modulus_bytes = (n.bit_length() + 7) // 8
    pad_len = modulus_bytes - len(digest_info) - 3
    em = b"\x00\x01" + b"\xff" * pad_len + b"\x00" + digest_info
    m = int.from_bytes(em, "big")
    c = pow(m, d, n)
    sig_bytes = c.to_bytes(modulus_bytes, "big")

    import base64

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("response.txt", response)
        zf.writestr("canonical.bin", canonical)
        zf.writestr("hash.sha256", h_hex)
        zf.writestr("signature.sig", base64.b64encode(sig_bytes))
        zf.writestr("timestamp.tsr", b"Zm91")  # non-empty placeholder
        zf.writestr("metadata.json", json.dumps({"model": "external", "policyVersion": "1.0"}).encode())
        zf.writestr("public_key.pem", pub_pem)
    return buf.getvalue(), priv, h


def _write(tmp_path: Path, name: str, blob: bytes) -> str:
    p = tmp_path / name
    p.write_bytes(blob)
    return str(p)


# ─── happy paths ────────────────────────────────────────────────────────


def test_verify_accepts_self_consistent_composite_bundle(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    p = _write(tmp_path, "evidence.aep", blob)
    r = EvidenceAPI().verify(p)
    assert isinstance(r, EvidenceVerifyResult)
    assert r.outcome == "valid"
    assert r.response_canonical_bytes == len("test response\n")
    assert r.unsigned_suffix_bytes > 0
    assert r.metadata == {"model": "external", "policyVersion": "1.0"}
    assert r.signature_bytes == 256


def test_verify_accepts_sign_only_bundle_no_claim(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle(composite=False)
    p = _write(tmp_path, "e.aep", blob)
    r = EvidenceAPI().verify(p)
    assert r.outcome == "valid"
    assert r.unsigned_suffix_bytes == 0


# ─── tamper detection ──────────────────────────────────────────────────


def _modify_zip(blob: bytes, mutate) -> bytes:
    """Helper: read a zip, apply mutate(name->bytes-dict), return new zip."""
    src = zipfile.ZipFile(io.BytesIO(blob))
    contents = {n: src.read(n) for n in src.namelist()}
    src.close()
    contents = mutate(contents) or contents
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for n, b in contents.items():
            zf.writestr(n, b)
    return out.getvalue()


def test_verify_reports_missing_files(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    def drop(c):
        c.pop("signature.sig")
        return c
    p = _write(tmp_path, "broken.aep", _modify_zip(blob, drop))
    r = EvidenceAPI().verify(p)
    assert r.outcome == "missing_files"
    assert r.missing == ["signature.sig"]


def test_verify_reports_hash_mismatch_when_hash_overwritten(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    def overwrite(c):
        c["hash.sha256"] = b"0" * 64
        return c
    p = _write(tmp_path, "bad-hash.aep", _modify_zip(blob, overwrite))
    r = EvidenceAPI().verify(p)
    assert r.outcome == "hash_mismatch"
    assert r.expected_hash == "0" * 64
    assert r.computed_hash and r.computed_hash != r.expected_hash


def test_verify_reports_signature_invalid_when_signature_replaced(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    def replace(c):
        # 256 bytes of arbitrary content, base64-encoded — wrong shape, will
        # fail PKCS#1 v1.5 unpad.
        import base64
        c["signature.sig"] = base64.b64encode(b"\x00" * 256)
        return c
    p = _write(tmp_path, "bad-sig.aep", _modify_zip(blob, replace))
    r = EvidenceAPI().verify(p)
    assert r.outcome == "signature_invalid"


def test_verify_reports_tsa_empty_when_timestamp_zero_length(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    def zero(c):
        c["timestamp.tsr"] = b""
        return c
    p = _write(tmp_path, "no-tsa.aep", _modify_zip(blob, zero))
    r = EvidenceAPI().verify(p)
    assert r.outcome == "tsa_empty"


def test_verify_reports_metadata_invalid_when_metadata_not_json(tmp_path: Path) -> None:
    blob, _, _ = _build_bundle()
    def break_meta(c):
        c["metadata.json"] = b"not a json"
        return c
    p = _write(tmp_path, "bad-meta.aep", _modify_zip(blob, break_meta))
    r = EvidenceAPI().verify(p)
    assert r.outcome == "metadata_invalid"


def test_verify_raises_on_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        EvidenceAPI().verify(str(tmp_path / "does-not-exist.aep"))


def test_verify_reports_zip_invalid_on_non_zip_file(tmp_path: Path) -> None:
    p = _write(tmp_path, "garbage.aep", b"not a zip")
    r = EvidenceAPI().verify(p)
    assert r.outcome == "zip_invalid"


# ─── client wiring ─────────────────────────────────────────────────────


def test_aletheia_client_exposes_evidence_attribute() -> None:
    from aletheia import AletheiaClient

    c = AletheiaClient(base_url="https://api.example.com", token="t")
    assert hasattr(c, "evidence")
    assert hasattr(c.evidence, "verify")


def test_evidence_bundle_files_constant_matches_required_layout() -> None:
    # Pinned so a typo in the required AEP entries gets caught by SDK tests too.
    assert EVIDENCE_BUNDLE_FILES == (
        "response.txt",
        "canonical.bin",
        "hash.sha256",
        "signature.sig",
        "timestamp.tsr",
        "metadata.json",
        "public_key.pem",
    )
