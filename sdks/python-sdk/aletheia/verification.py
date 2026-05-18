"""
Verification API - Cryptographic evidence verification
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from .models import VerificationResult

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient


class VerificationAPI:
    """Synchronous Verification API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def verify_evidence(self, evidence_file: str) -> VerificationResult:
        """
        Verify cryptographic evidence package
        
        Args:
            evidence_file: Path to .aep evidence file
            
        Returns:
            VerificationResult with validation details
        """
        # Read evidence file
        with open(evidence_file, "rb") as f:
            evidence_data = f.read()

        # Upload for verification
        # Note: This is a simplified implementation
        # In production, you'd use multipart/form-data upload
        import base64
        encoded = base64.b64encode(evidence_data).decode("utf-8")

        data = self._client.request(
            "POST",
            "/api/v1/verification/verify",
            json={"evidence": encoded},
        )

        return VerificationResult(**data)

    def verify_signature(
        self, 
        event_id: str,
        signature: str,
        public_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify event signature
        
        Args:
            event_id: Event identifier
            signature: Signature to verify
            public_key: Optional public key (otherwise uses agent's key)
            
        Returns:
            Verification result
        """
        data = self._client.request(
            "POST",
            f"/api/v1/verification/events/{event_id}/signature",
            json={
                "signature": signature,
                "publicKey": public_key,
            },
        )
        return data

    def verify_timestamp(self, event_id: str, timestamp_proof: str) -> Dict[str, Any]:
        """
        Verify RFC 3161 timestamp
        
        Args:
            event_id: Event identifier
            timestamp_proof: Timestamp proof to verify
            
        Returns:
            Verification result
        """
        data = self._client.request(
            "POST",
            f"/api/v1/verification/events/{event_id}/timestamp",
            json={"timestampProof": timestamp_proof},
        )
        return data

    def verify_chain_of_custody(self, event_id: str) -> Dict[str, Any]:
        """
        Verify event chain of custody
        
        Args:
            event_id: Event identifier
            
        Returns:
            Chain of custody verification result
        """
        data = self._client.request(
            "GET",
            f"/api/v1/verification/events/{event_id}/custody",
        )
        return data


class AsyncVerificationAPI:
    """Asynchronous Verification API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def verify_evidence(self, evidence_file: str) -> VerificationResult:
        """Async: Verify cryptographic evidence package"""
        # Read evidence file
        with open(evidence_file, "rb") as f:
            evidence_data = f.read()

        import base64
        encoded = base64.b64encode(evidence_data).decode("utf-8")

        data = await self._client.request(
            "POST",
            "/api/v1/verification/verify",
            json={"evidence": encoded},
        )

        return VerificationResult(**data)

    async def verify_signature(
        self, 
        event_id: str,
        signature: str,
        public_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async: Verify event signature"""
        data = await self._client.request(
            "POST",
            f"/api/v1/verification/events/{event_id}/signature",
            json={
                "signature": signature,
                "publicKey": public_key,
            },
        )
        return data

    async def verify_timestamp(self, event_id: str, timestamp_proof: str) -> Dict[str, Any]:
        """Async: Verify RFC 3161 timestamp"""
        data = await self._client.request(
            "POST",
            f"/api/v1/verification/events/{event_id}/timestamp",
            json={"timestampProof": timestamp_proof},
        )
        return data

    async def verify_chain_of_custody(self, event_id: str) -> Dict[str, Any]:
        """Async: Verify event chain of custody"""
        data = await self._client.request(
            "GET",
            f"/api/v1/verification/events/{event_id}/custody",
        )
        return data
