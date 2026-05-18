"""
Audit API - Event logging and audit trail
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from .models import AuditEvent, AuditEventCreate, AuditEventList

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient


class AuditAPI:
    """Synchronous Audit API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def log_event(
        self,
        agent_id: str,
        event_type: str,
        action: str,
        outcome: str,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        risk_level: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> AuditEvent:
        """
        Log an audit event
        
        Args:
            agent_id: Agent identifier
            event_type: AuditEventType name (e.g. COMPLIANCE_CHECK_PASSED, POLICY_EVALUATED)
            action: Action performed
            outcome: Outcome (SUCCESS, FAILURE, etc.)
            resource: Resource affected (optional)
            metadata: Additional metadata
            risk_level: Risk level (low, medium, high)
            user_id: User who triggered the event
            
        Returns:
            Created AuditEvent object
        """
        request = AuditEventCreate(
            agent_id=agent_id,
            event_type=event_type,
            action=action,
            outcome=outcome,
            resource=resource,
            metadata=metadata,
            risk_level=risk_level,
            user_id=user_id,
        )

        data = self._client.request(
            "POST",
            "/api/v1/audit/events",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return AuditEvent(**data)

    def get_event(self, event_id: str) -> AuditEvent:
        """
        Get audit event by ID
        
        Args:
            event_id: Event identifier
            
        Returns:
            AuditEvent object
        """
        data = self._client.request("GET", f"/api/v1/audit/events/{event_id}")
        return AuditEvent(**data)

    def list_events(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_level: Optional[str] = None,
        outcome: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """
        List audit events with filters
        
        Args:
            agent_id: Filter by agent
            event_type: Filter by event type
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            risk_level: Filter by risk level
            outcome: Filter by outcome
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of AuditEvent objects
        """
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agentId"] = agent_id
        if event_type:
            params["eventType"] = event_type
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if risk_level:
            params["riskLevel"] = risk_level
        if outcome:
            params["outcome"] = outcome

        data = self._client.request("GET", "/api/v1/audit/events", params=params)
        
        # Handle different response formats
        if isinstance(data, list):
            return [AuditEvent(**item) for item in data]
        elif "events" in data:
            return [AuditEvent(**item) for item in data["events"]]
        elif "items" in data:
            return [AuditEvent(**item) for item in data["items"]]
        return []

    def download_evidence(self, event_id: str) -> bytes:
        """
        Fetches audit event JSON (GET /api/v1/audit/events/{id}).
        For verifiable AI Evidence Packages (.aep), use GET /api/ai/evidence/{responseId} instead.
        """
        return self._client.download(f"/api/v1/audit/events/{event_id}")

    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Search audit events
        
        Args:
            query: Search query
            filters: Additional filters
            limit: Maximum results
            
        Returns:
            List of matching AuditEvent objects
        """
        params = {"q": query, "limit": limit}
        if filters:
            params.update(filters)

        data = self._client.request("GET", "/api/v1/audit/search", params=params)
        
        if isinstance(data, list):
            return [AuditEvent(**item) for item in data]
        elif "events" in data or "results" in data:
            items = data.get("events") or data.get("results") or []
            return [AuditEvent(**item) for item in items]
        return []


class AsyncAuditAPI:
    """Asynchronous Audit API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def log_event(
        self,
        agent_id: str,
        event_type: str,
        action: str,
        outcome: str,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        risk_level: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> AuditEvent:
        """Async: Log an audit event"""
        request = AuditEventCreate(
            agent_id=agent_id,
            event_type=event_type,
            action=action,
            outcome=outcome,
            resource=resource,
            metadata=metadata,
            risk_level=risk_level,
            user_id=user_id,
        )

        data = await self._client.request(
            "POST",
            "/api/v1/audit/events",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return AuditEvent(**data)

    async def get_event(self, event_id: str) -> AuditEvent:
        """Async: Get audit event by ID"""
        data = await self._client.request("GET", f"/api/v1/audit/events/{event_id}")
        return AuditEvent(**data)

    async def list_events(
        self,
        agent_id: Optional[str] = None,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        risk_level: Optional[str] = None,
        outcome: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditEvent]:
        """Async: List audit events with filters"""
        params = {"limit": limit, "offset": offset}
        if agent_id:
            params["agentId"] = agent_id
        if event_type:
            params["eventType"] = event_type
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if risk_level:
            params["riskLevel"] = risk_level
        if outcome:
            params["outcome"] = outcome

        data = await self._client.request("GET", "/api/v1/audit/events", params=params)
        
        if isinstance(data, list):
            return [AuditEvent(**item) for item in data]
        elif "events" in data:
            return [AuditEvent(**item) for item in data["events"]]
        elif "items" in data:
            return [AuditEvent(**item) for item in data["items"]]
        return []

    async def download_evidence(self, event_id: str) -> bytes:
        """Async: audit event JSON bytes (GET /api/v1/audit/events/{id})."""
        return await self._client.download(f"/api/v1/audit/events/{event_id}")

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """Async: Search audit events"""
        params = {"q": query, "limit": limit}
        if filters:
            params.update(filters)

        data = await self._client.request("GET", "/api/v1/audit/search", params=params)
        
        if isinstance(data, list):
            return [AuditEvent(**item) for item in data]
        elif "events" in data or "results" in data:
            items = data.get("events") or data.get("results") or []
            return [AuditEvent(**item) for item in items]
        return []
