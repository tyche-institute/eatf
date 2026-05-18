"""
Attestations API — partner-facing /api/v1/attest wrapper.

Full ATAP attestation for an agent action: canonicalize → sign (PQC Dilithium) →
temporal anchor (TSA) → policy evaluate → persist. Returns a signed `attestationId`
plus canonical hash, temporal anchors, and policy-evaluation result.

Also exposes the policy-registry discovery endpoint so callers can pick a valid
`policy_id` without reading backend migrations.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient


class AttestationsAPI:
    """Synchronous Attestations API."""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def list_policies(self) -> List[Dict[str, Any]]:
        """
        List ATAP policies accepted by :meth:`attest` (``GET /api/v1/policy-registry``).

        Returns a list of ``{policyId, policyVersion, name, description}`` entries.
        These are the only ``policy_id`` values that ``/api/v1/attest`` accepts —
        values from ``GET /api/v1/policies`` are coverage policies for a different
        feature and will be rejected.
        """
        return self._client.request("GET", "/api/v1/policy-registry")

    def attest(
        self,
        agent_id: str,
        action_type: str,
        input: str,
        output: str,
        policy_id: str,
        policy_version: str = "1.0",
        privacy_mode: bool = False,
        strict_policy_mode: bool = False,
        include_compliance_report: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Attest an agent action.

        Args:
            agent_id: Full URN-form id from ``POST /api/v1/agents/register``
                (e.g. ``urn:uuid:<uuid>``). A bare UUID will be rejected.
            action_type: Short identifier for the kind of action, e.g.
                ``"EU_AI_ACT_ADVISORY"``.
            input: User prompt or action input (canonicalized + hashed).
            output: Agent response or action output (canonicalized + signed).
            policy_id: One of the ids returned by :meth:`list_policies`
                (``atap-basic``, ``atap-minimal``, ``atap-high-risk``).
            policy_version: Policy version, defaults to ``"1.0"``.
            privacy_mode: If True, ``input`` / ``output`` are hashed before
                storage so only the digests persist.
            strict_policy_mode: If True, a failing critical rule aborts the
                attestation instead of recording a partial-compliance result.
            include_compliance_report: If True, the response embeds a rendered
                compliance summary (EU AI Act / ISO 42001 mappings).
            metadata: Optional free-form metadata attached to the attestation.

        Returns:
            The full :class:`AttestationResult` dict (``attestationId``,
            ``canonicalHash``, ``signatures``, ``temporalAnchors``,
            ``policyEvaluation``, ``createdAt``).

        Raises:
            aletheia.exceptions.ValidationError: If any required field is blank,
                the agent is not on the caller's tenant, or the policy is
                unknown. The error message will point at
                ``GET /api/v1/policy-registry`` when relevant.
        """
        body: Dict[str, Any] = {
            "agentId": agent_id,
            "actionType": action_type,
            "input": input,
            "output": output,
            "policyId": policy_id,
            "policyVersion": policy_version,
            "privacyMode": privacy_mode,
            "strictPolicyMode": strict_policy_mode,
            "includeComplianceReport": include_compliance_report,
        }
        if metadata is not None:
            body["metadata"] = metadata
        return self._client.request("POST", "/api/v1/attest", json=body)


class AsyncAttestationsAPI:
    """Asynchronous Attestations API — mirrors :class:`AttestationsAPI`."""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def list_policies(self) -> List[Dict[str, Any]]:
        return await self._client.request("GET", "/api/v1/policy-registry")

    async def attest(
        self,
        agent_id: str,
        action_type: str,
        input: str,
        output: str,
        policy_id: str,
        policy_version: str = "1.0",
        privacy_mode: bool = False,
        strict_policy_mode: bool = False,
        include_compliance_report: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "agentId": agent_id,
            "actionType": action_type,
            "input": input,
            "output": output,
            "policyId": policy_id,
            "policyVersion": policy_version,
            "privacyMode": privacy_mode,
            "strictPolicyMode": strict_policy_mode,
            "includeComplianceReport": include_compliance_report,
        }
        if metadata is not None:
            body["metadata"] = metadata
        return await self._client.request("POST", "/api/v1/attest", json=body)
