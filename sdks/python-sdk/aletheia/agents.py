"""
Agents API - Agent lifecycle management
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from .exceptions import AgentTenantConflictError, AletheiaAPIError
from .models import Agent, AgentCreate, AgentEnsureRequest, AgentUpdate, EnsureResult

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient


# Recommended values for the free-form ``agent_type`` field on
# ``POST /api/v1/agents/register``. The backend stores the string verbatim,
# so passing other values still works — these names exist purely so partner
# code, dashboards, and policy rules can group agents by intent.
AGENT_TYPE_CONVERSATIONAL = "CONVERSATIONAL"
AGENT_TYPE_ANALYTICAL = "ANALYTICAL"
AGENT_TYPE_ROBOTIC = "ROBOTIC"
AGENT_TYPE_DATASET_PUBLISHER = "DATASET_PUBLISHER"
"""
Periodic dataset/model snapshot publishers (e.g. h2oatlas.ee).

These agents do not take autonomous actions; they emit signed snapshots on a
schedule. Use ``risk_classification="limited"`` and tag capabilities such as
``periodic_snapshot`` and ``ml_pipeline``. The backend treats this type as
low action-risk and does not require a human-approval workflow.
"""

CAPABILITY_PERIODIC_SNAPSHOT = "periodic_snapshot"
CAPABILITY_ML_PIPELINE = "ml_pipeline"


class AgentsAPI:
    """Synchronous Agents API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def create(
        self,
        name: str,
        agent_type: str,
        risk_classification: str = "limited",
        capabilities: Optional[List[str]] = None,
        primary_jurisdiction: str = "EU",
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """
        Register a new AI agent.

        Args:
            name: Agent name
            agent_type: Type. Recommended values:
                ``CONVERSATIONAL`` (chatbots, assistants),
                ``ANALYTICAL`` (decision-support, scoring),
                ``ROBOTIC`` (physical actuators),
                ``DATASET_PUBLISHER`` (periodic ML/data snapshots — e.g. h2oatlas.ee).
                Any other string is also accepted; the constants above
                (``AGENT_TYPE_*``) are exported for convenience.
            risk_classification: minimal, limited, or high
            capabilities: List of capability tags. For DATASET_PUBLISHER use
                ``[CAPABILITY_PERIODIC_SNAPSHOT, CAPABILITY_ML_PIPELINE]``.
            primary_jurisdiction: Primary jurisdiction (default: EU)
            description: Optional description

        Returns:
            Created Agent object
        """
        request = AgentCreate(
            name=name,
            agent_type=agent_type,
            risk_classification=risk_classification,
            capabilities=capabilities or [],
            primary_jurisdiction=primary_jurisdiction,
            description=description,
            metadata=kwargs.get("metadata"),
        )

        data = self._client.request(
            "POST",
            "/api/v1/agents/register",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return Agent(**data)

    def get(self, agent_id: str) -> Agent:
        """
        Get agent by ID
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent object
        """
        data = self._client.request("GET", f"/api/v1/agents/{agent_id}")
        return Agent(**data)

    def list(
        self,
        status: Optional[str] = None,
        agent_type: Optional[str] = None,
        risk_classification: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Agent]:
        """
        List agents with optional filters
        
        Args:
            status: Filter by status
            agent_type: Filter by type
            risk_classification: Filter by risk level
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of Agent objects
        """
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if agent_type:
            params["agentType"] = agent_type
        if risk_classification:
            params["riskClassification"] = risk_classification

        data = self._client.request("GET", "/api/v1/agents", params=params)
        
        # Handle both list and paginated response
        if isinstance(data, list):
            return [Agent(**item) for item in data]
        elif "items" in data or "agents" in data:
            items = data.get("items") or data.get("agents") or []
            return [Agent(**item) for item in items]
        return []

    def update(self, agent_id: str, **kwargs) -> Agent:
        """
        Update agent properties
        
        Args:
            agent_id: Agent identifier
            **kwargs: Fields to update (name, status, etc.)
            
        Returns:
            Updated Agent object
        """
        request = AgentUpdate(**kwargs)
        data = self._client.request(
            "PUT",
            f"/api/v1/agents/{agent_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Agent(**data)

    def delete(self, agent_id: str) -> None:
        """
        Delete agent
        
        Args:
            agent_id: Agent identifier
        """
        self._client.request("DELETE", f"/api/v1/agents/{agent_id}")

    def deactivate(self, agent_id: str) -> Agent:
        """
        Deactivate agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Updated Agent object
        """
        return self.update(agent_id, status="inactive")

    def activate(self, agent_id: str) -> Agent:
        """
        Activate agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Updated Agent object
        """
        return self.update(agent_id, status="active")

    def get_certificate(self, agent_id: str) -> bytes:
        """
        GET /api/v1/certificates/{agentId} (returns JSON list; raw response bytes).
        """
        return self._client.download(f"/api/v1/certificates/{agent_id}")

    def ensure(
        self,
        agent_id: str,
        *,
        display_name: str,
        agent_type: str,
        risk_classification: str,
        description: Optional[str] = None,
        organization: Optional[str] = None,
        contact_email: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        eidas_certificate_arn: Optional[str] = None,
        eidas_level: Optional[str] = None,
        signature_algorithm: Optional[str] = None,
        primary_jurisdiction: Optional[str] = None,
        transaction_limit: Optional[float] = None,
        transaction_currency: Optional[str] = None,
        mcp_did: Optional[str] = None,
    ) -> EnsureResult:
        """Idempotently register or patch an agent by caller-supplied ``agent_id``.

        Implements the manifest pattern from the AEP profile v1 spec:
        the first call creates the agent on the caller's tenant (HTTP 201),
        subsequent calls patch mutable fields in place (HTTP 200). The eIDAS
        certificate is issued on create and is **not** re-issued on update.

        Args:
            agent_id: Caller-chosen stable identifier. Either a ``urn:uuid:`` URN
                or a namespaced slug like ``eatf-demo:my-agent``. Must be ≤255
                characters and contain no whitespace.
            display_name: Human-readable name (maps to the server's ``name``).
            agent_type: Type taxonomy (e.g. ``custom``, ``conversational``).
            risk_classification: ``minimal``, ``limited``, or ``high``.
            description, organization, contact_email, capabilities,
            eidas_certificate_arn, eidas_level, signature_algorithm,
            primary_jurisdiction, transaction_limit, transaction_currency,
            mcp_did: Optional fields. Null fields leave existing values
                untouched on update.

        Returns:
            :class:`EnsureResult` with the persisted :class:`Agent` and a
            ``created`` flag (``True`` on insert, ``False`` on in-place patch).

        Raises:
            AgentTenantConflictError: If the requested ``agent_id`` already
                exists on a different tenant.
            ValidationError: If the manifest fails server-side validation.
            AletheiaAPIError: For other API errors (auth, server, network).
        """
        request = AgentEnsureRequest(
            name=display_name,
            description=description,
            organization=organization,
            contact_email=contact_email,
            agent_type=agent_type,
            risk_classification=risk_classification,
            capabilities=capabilities,
            eidas_certificate_arn=eidas_certificate_arn,
            eidas_level=eidas_level,
            signature_algorithm=signature_algorithm,
            primary_jurisdiction=primary_jurisdiction,
            transaction_limit=transaction_limit,
            transaction_currency=transaction_currency,
            mcp_did=mcp_did,
        )
        body: Dict[str, Any] = request.model_dump(by_alias=True, exclude_none=True)
        try:
            data, status = self._client.request_with_status(
                "PUT",
                f"/api/v1/agents/{agent_id}",
                json=body,
            )
        except AletheiaAPIError as exc:
            if getattr(exc, "status_code", None) == 409:
                raise AgentTenantConflictError(
                    str(exc) or "agentId already in use on a different tenant",
                    status_code=409,
                    response=exc.response,
                    agent_id=agent_id,
                ) from exc
            raise

        return EnsureResult(agent=Agent(**data), created=(status == 201))


class AsyncAgentsAPI:
    """Asynchronous Agents API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def create(
        self,
        name: str,
        agent_type: str,
        risk_classification: str = "limited",
        capabilities: Optional[List[str]] = None,
        primary_jurisdiction: str = "EU",
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """Async: Register a new AI agent"""
        request = AgentCreate(
            name=name,
            agent_type=agent_type,
            risk_classification=risk_classification,
            capabilities=capabilities or [],
            primary_jurisdiction=primary_jurisdiction,
            description=description,
            metadata=kwargs.get("metadata"),
        )

        data = await self._client.request(
            "POST",
            "/api/v1/agents/register",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return Agent(**data)

    async def get(self, agent_id: str) -> Agent:
        """Async: Get agent by ID"""
        data = await self._client.request("GET", f"/api/v1/agents/{agent_id}")
        return Agent(**data)

    async def list(
        self,
        status: Optional[str] = None,
        agent_type: Optional[str] = None,
        risk_classification: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Agent]:
        """Async: List agents with optional filters"""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if agent_type:
            params["agentType"] = agent_type
        if risk_classification:
            params["riskClassification"] = risk_classification

        data = await self._client.request("GET", "/api/v1/agents", params=params)
        
        if isinstance(data, list):
            return [Agent(**item) for item in data]
        elif "items" in data or "agents" in data:
            items = data.get("items") or data.get("agents") or []
            return [Agent(**item) for item in items]
        return []

    async def update(self, agent_id: str, **kwargs) -> Agent:
        """Async: Update agent properties"""
        request = AgentUpdate(**kwargs)
        data = await self._client.request(
            "PUT",
            f"/api/v1/agents/{agent_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return Agent(**data)

    async def delete(self, agent_id: str) -> None:
        """Async: Delete agent"""
        await self._client.request("DELETE", f"/api/v1/agents/{agent_id}")

    async def deactivate(self, agent_id: str) -> Agent:
        """Async: Deactivate agent"""
        return await self.update(agent_id, status="inactive")

    async def activate(self, agent_id: str) -> Agent:
        """Async: Activate agent"""
        return await self.update(agent_id, status="active")

    async def get_certificate(self, agent_id: str) -> bytes:
        """Async: Download raw JSON bytes for agent certificates listing."""
        return await self._client.download(f"/api/v1/certificates/{agent_id}")

    async def ensure(
        self,
        agent_id: str,
        *,
        display_name: str,
        agent_type: str,
        risk_classification: str,
        description: Optional[str] = None,
        organization: Optional[str] = None,
        contact_email: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        eidas_certificate_arn: Optional[str] = None,
        eidas_level: Optional[str] = None,
        signature_algorithm: Optional[str] = None,
        primary_jurisdiction: Optional[str] = None,
        transaction_limit: Optional[float] = None,
        transaction_currency: Optional[str] = None,
        mcp_did: Optional[str] = None,
    ) -> EnsureResult:
        """Async variant of :meth:`AgentsAPI.ensure`. See sync docstring for semantics."""
        request = AgentEnsureRequest(
            name=display_name,
            description=description,
            organization=organization,
            contact_email=contact_email,
            agent_type=agent_type,
            risk_classification=risk_classification,
            capabilities=capabilities,
            eidas_certificate_arn=eidas_certificate_arn,
            eidas_level=eidas_level,
            signature_algorithm=signature_algorithm,
            primary_jurisdiction=primary_jurisdiction,
            transaction_limit=transaction_limit,
            transaction_currency=transaction_currency,
            mcp_did=mcp_did,
        )
        body: Dict[str, Any] = request.model_dump(by_alias=True, exclude_none=True)
        try:
            data, status = await self._client.request_with_status(
                "PUT",
                f"/api/v1/agents/{agent_id}",
                json=body,
            )
        except AletheiaAPIError as exc:
            if getattr(exc, "status_code", None) == 409:
                raise AgentTenantConflictError(
                    str(exc) or "agentId already in use on a different tenant",
                    status_code=409,
                    response=exc.response,
                    agent_id=agent_id,
                ) from exc
            raise

        return EnsureResult(agent=Agent(**data), created=(status == 201))
