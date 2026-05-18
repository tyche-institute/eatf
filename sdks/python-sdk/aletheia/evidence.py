"""
Evidence API — offline verification of EATF .aep evidence packages.

Mirrors the behaviour of `eatf verify` from the @eatf/cli Node tool: opens
the zip, checks the required entries, recomputes SHA-256 over the
response_canonical prefix (handling the composite `response + '\\n' + claim`
form the backend produces), recovers the digest from the RSA signature
via raw modular exponentiation, and compares it to the recomputed hash.

Why raw modular exponentiation rather than `cryptography`'s high-level
`public_key.verify(...)`: the EATF backend's SignatureServiceImpl
hand-rolls the SHA-256 DigestInfo and omits the standard `05 00` NULL
parameters in the AlgorithmIdentifier, producing a 49-byte DigestInfo
instead of the standard 51-byte form. `cryptography`'s strict PKCS1v15
verifier rejects this even though the signature is mathematically valid.
We match the JS CLI's workaround: PEM-parse the public key for n + e,
do `pow(c, e, n)`, strip PKCS#1 v1.5 padding, extract the trailing
32-byte digest. Same security guarantee (signature binds to the digest;
digest binds to the data via SHA-256 over response_canonical).

`cryptography` is an optional dependency declared under the
``aletheia-ai[verify]`` extra. If it's not importable, calls raise
:class:`EvidenceVerifyDependencyError` with install instructions
rather than crashing on a confusing import error.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


EVIDENCE_BUNDLE_FILES = (
    "response.txt",
    "canonical.bin",
    "hash.sha256",
    "signature.sig",
    "timestamp.tsr",
    "metadata.json",
    "public_key.pem",
)
"""The required entries every EATF .aep zip must contain."""


@dataclass
class EvidenceVerifyResult:
    """Outcome of :meth:`EvidenceAPI.verify`."""

    outcome: str
    """One of: ``valid``, ``missing_files``, ``hash_mismatch``,
    ``signature_invalid``, ``tsa_empty``, ``metadata_invalid``,
    ``zip_invalid``."""

    path: str
    """Absolute path to the .aep file that was checked."""

    hash: Optional[str] = None
    """Hex SHA-256 digest from ``hash.sha256``."""

    canonical_bytes: int = 0
    response_canonical_bytes: int = 0
    unsigned_suffix_bytes: int = 0
    signature_bytes: int = 0
    tsa_token_bytes: int = 0

    metadata: Optional[Dict[str, Any]] = None
    missing: List[str] = field(default_factory=list)
    expected_hash: Optional[str] = None
    computed_hash: Optional[str] = None
    error: Optional[str] = None


class EvidenceVerifyDependencyError(RuntimeError):
    """Raised when ``cryptography`` is not installed."""

    def __init__(self) -> None:
        super().__init__(
            "Offline evidence verification requires the `cryptography` package. "
            "Install with `pip install aletheia-ai[verify]` or `pip install cryptography`."
        )


_CLAIM_BOUNDARY = b'\n{"claim":"'


def _resolve_response_canonical(canonical: bytes, expected_hash_hex: str) -> tuple[bytes, str]:
    """
    Find the bytes whose SHA-256 the backend stored as hash.sha256.

    The backend's AiEvidenceController writes
    ``canonical.bin = response_canonical + b'\\n' + claim_envelope`` whenever
    ``claim`` or ``policyVersion`` is set on the AiResponse, while
    ``hash.sha256`` covers ONLY the ``response_canonical`` prefix. We try
    the simple case first; on mismatch, locate the last ``\\n{"claim":"``
    boundary (alphabetical-first key in ClaimCanonical) and re-hash the
    prefix.

    Returns ``(response_canonical_bytes, computed_hash_hex)``.
    """
    h = hashlib.sha256(canonical).hexdigest()
    if h == expected_hash_hex:
        return canonical, h
    idx = canonical.rfind(_CLAIM_BOUNDARY)
    if idx > 0:
        prefix = canonical[:idx]
        h2 = hashlib.sha256(prefix).hexdigest()
        return prefix, h2
    return canonical, h


def _rsa_recover_digest(public_key_pem: bytes, signature_bytes: bytes) -> bytes:
    """
    Decrypt an RSA-PKCS#1-v1.5 signature with the public key and return
    the trailing 32 bytes (the SHA-256 digest the signer wrapped in a
    DigestInfo). Tolerates the backend's non-standard 49-byte DigestInfo.
    """
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
    except ImportError as exc:  # pragma: no cover — exercised in CI without the extra
        raise EvidenceVerifyDependencyError() from exc

    pub = serialization.load_pem_public_key(public_key_pem)
    if not isinstance(pub, RSAPublicKey):
        raise ValueError("public_key.pem is not an RSA key")
    nums = pub.public_numbers()
    n = nums.n
    e = nums.e

    modulus_bytes = (n.bit_length() + 7) // 8
    if len(signature_bytes) != modulus_bytes:
        raise ValueError(
            f"signature length {len(signature_bytes)} does not match modulus size {modulus_bytes}"
        )

    c = int.from_bytes(signature_bytes, "big")
    m = pow(c, e, n)
    m_bytes = m.to_bytes(modulus_bytes, "big")

    # PKCS#1 v1.5 signature padding: 0x00 0x01 [0xFF...0xFF] 0x00 <DigestInfo>
    if len(m_bytes) < 11 or m_bytes[0] != 0 or m_bytes[1] != 1:
        raise ValueError("recovered plaintext lacks PKCS#1 v1.5 signature header")
    try:
        sep = m_bytes.index(0, 2)
    except ValueError as exc:
        raise ValueError("PKCS#1 v1.5 padding has no terminator") from exc
    digest_info = m_bytes[sep + 1 :]
    if len(digest_info) < 32:
        raise ValueError(f"recovered DigestInfo too short ({len(digest_info)} bytes)")
    return digest_info[-32:]


class EvidenceAPI:
    """Offline verification of .aep evidence packages."""

    def verify(self, path: str) -> EvidenceVerifyResult:
        """
        Verify a downloaded .aep evidence bundle without contacting the backend.

        Args:
            path: Path to the .aep zip file.

        Returns:
            :class:`EvidenceVerifyResult` with ``outcome`` set to one of
            ``valid``, ``missing_files``, ``hash_mismatch``,
            ``signature_invalid``, ``tsa_empty``, ``metadata_invalid``,
            ``zip_invalid``. Cryptographic failures do NOT raise — callers
            always get a structured outcome. I/O errors (missing file,
            unreadable zip) DO raise.

        Raises:
            FileNotFoundError: if ``path`` does not exist.
            EvidenceVerifyDependencyError: if the optional ``cryptography``
                dependency is not installed.
        """
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(abs_path)

        try:
            zf = zipfile.ZipFile(abs_path)
        except zipfile.BadZipFile as exc:
            return EvidenceVerifyResult(outcome="zip_invalid", path=abs_path, error=str(exc))

        try:
            names = set(zf.namelist())
            missing = [n for n in EVIDENCE_BUNDLE_FILES if n not in names]
            if missing:
                return EvidenceVerifyResult(
                    outcome="missing_files", path=abs_path, missing=list(missing)
                )

            canonical = zf.read("canonical.bin")
            expected_hash = zf.read("hash.sha256").decode("utf-8").strip()
            response_canonical, computed_hash = _resolve_response_canonical(canonical, expected_hash)
            if computed_hash != expected_hash:
                return EvidenceVerifyResult(
                    outcome="hash_mismatch",
                    path=abs_path,
                    expected_hash=expected_hash,
                    computed_hash=computed_hash,
                )

            signature_b64 = zf.read("signature.sig").decode("utf-8").strip()
            try:
                import base64

                signature_bytes = base64.b64decode(signature_b64, validate=True)
            except Exception as exc:
                return EvidenceVerifyResult(
                    outcome="signature_invalid",
                    path=abs_path,
                    error=f"signature.sig is not valid base64: {exc}",
                    hash=expected_hash,
                )
            public_key_pem = zf.read("public_key.pem")

            try:
                recovered = _rsa_recover_digest(public_key_pem, signature_bytes)
            except EvidenceVerifyDependencyError:
                raise
            except Exception as exc:
                return EvidenceVerifyResult(
                    outcome="signature_invalid",
                    path=abs_path,
                    error=str(exc),
                    hash=expected_hash,
                    signature_bytes=len(signature_bytes),
                )

            recovered_hex = recovered.hex()
            if recovered_hex != expected_hash:
                return EvidenceVerifyResult(
                    outcome="signature_invalid",
                    path=abs_path,
                    error=f"digest in signature ({recovered_hex}) does not match hash.sha256",
                    hash=expected_hash,
                    signature_bytes=len(signature_bytes),
                )

            tsa = zf.read("timestamp.tsr")
            if not tsa:
                return EvidenceVerifyResult(
                    outcome="tsa_empty",
                    path=abs_path,
                    hash=expected_hash,
                    signature_bytes=len(signature_bytes),
                )

            try:
                metadata = json.loads(zf.read("metadata.json"))
            except json.JSONDecodeError as exc:
                return EvidenceVerifyResult(
                    outcome="metadata_invalid", path=abs_path, error=str(exc)
                )

            return EvidenceVerifyResult(
                outcome="valid",
                path=abs_path,
                hash=expected_hash,
                canonical_bytes=len(canonical),
                response_canonical_bytes=len(response_canonical),
                unsigned_suffix_bytes=len(canonical) - len(response_canonical),
                signature_bytes=len(signature_bytes),
                tsa_token_bytes=len(tsa),
                metadata=metadata,
            )
        finally:
            zf.close()
