"""
Policies API - Policy management and enforcement
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from .models import Policy, PolicyCreate, PolicyRule

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient


class PoliciesAPI:
    """Synchronous Policies API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def create(
        self,
        name: str,
        jurisdiction: str,
        rules: List[Dict[str, Any]],
        description: Optional[str] = None,
        enabled: bool = True,
        **kwargs,
    ) -> Policy:
        """
        Create a compliance policy
        
        Args:
            name: Policy name
            jurisdiction: Jurisdiction (EU, US, etc.)
            rules: List of policy rules
            description: Optional description
            enabled: Whether policy is active
            
        Returns:
            Created Policy object
        """
        policy_rules = [PolicyRule(**rule) for rule in rules]
        
        request = PolicyCreate(
            name=name,
            jurisdiction=jurisdiction,
            rules=policy_rules,
            description=description,
            enabled=enabled,
            metadata=kwargs.get("metadata"),
        )

        data = self._client.request(
            "POST",
            "/api/v1/policies",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return Policy(**data)

    def get(self, policy_id: str) -> Policy:
        """
        Get policy by ID
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy object
        """
        data = self._client.request("GET", f"/api/v1/policies/{policy_id}")
        return Policy(**data)

    def list(
        self,
        jurisdiction: Optional[str] = None,
        enabled: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Policy]:
        """
        List policies with filters
        
        Args:
            jurisdiction: Filter by jurisdiction
            enabled: Filter by enabled status
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List of Policy objects
        """
        params = {"limit": limit, "offset": offset}
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if enabled is not None:
            params["enabled"] = enabled

        data = self._client.request("GET", "/api/v1/policies", params=params)
        
        if isinstance(data, list):
            return [Policy(**item) for item in data]
        elif "policies" in data or "items" in data:
            items = data.get("policies") or data.get("items") or []
            return [Policy(**item) for item in items]
        return []

    def update(self, policy_id: str, **kwargs) -> Policy:
        """
        Update policy
        
        Args:
            policy_id: Policy identifier
            **kwargs: Fields to update
            
        Returns:
            Updated Policy object
        """
        data = self._client.request(
            "PUT",
            f"/api/v1/policies/{policy_id}",
            json=kwargs,
        )
        return Policy(**data)

    def delete(self, policy_id: str) -> None:
        """
        Delete policy
        
        Args:
            policy_id: Policy identifier
        """
        self._client.request("DELETE", f"/api/v1/policies/{policy_id}")

    def enable(self, policy_id: str) -> Policy:
        """
        Enable policy
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Updated Policy object
        """
        return self.update(policy_id, enabled=True)

    def disable(self, policy_id: str) -> Policy:
        """
        Disable policy
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Updated Policy object
        """
        return self.update(policy_id, enabled=False)


class AsyncPoliciesAPI:
    """Asynchronous Policies API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def create(
        self,
        name: str,
        jurisdiction: str,
        rules: List[Dict[str, Any]],
        description: Optional[str] = None,
        enabled: bool = True,
        **kwargs,
    ) -> Policy:
        """Async: Create a compliance policy"""
        policy_rules = [PolicyRule(**rule) for rule in rules]
        
        request = PolicyCreate(
            name=name,
            jurisdiction=jurisdiction,
            rules=policy_rules,
            description=description,
            enabled=enabled,
            metadata=kwargs.get("metadata"),
        )

        data = await self._client.request(
            "POST",
            "/api/v1/policies",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

        return Policy(**data)

    async def get(self, policy_id: str) -> Policy:
        """Async: Get policy by ID"""
        data = await self._client.request("GET", f"/api/v1/policies/{policy_id}")
        return Policy(**data)

    async def list(
        self,
        jurisdiction: Optional[str] = None,
        enabled: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Policy]:
        """Async: List policies with filters"""
        params = {"limit": limit, "offset": offset}
        if jurisdiction:
            params["jurisdiction"] = jurisdiction
        if enabled is not None:
            params["enabled"] = enabled

        data = await self._client.request("GET", "/api/v1/policies", params=params)
        
        if isinstance(data, list):
            return [Policy(**item) for item in data]
        elif "policies" in data or "items" in data:
            items = data.get("policies") or data.get("items") or []
            return [Policy(**item) for item in items]
        return []

    async def update(self, policy_id: str, **kwargs) -> Policy:
        """Async: Update policy"""
        data = await self._client.request(
            "PUT",
            f"/api/v1/policies/{policy_id}",
            json=kwargs,
        )
        return Policy(**data)

    async def delete(self, policy_id: str) -> None:
        """Async: Delete policy"""
        await self._client.request("DELETE", f"/api/v1/policies/{policy_id}")

    async def enable(self, policy_id: str) -> Policy:
        """Async: Enable policy"""
        return await self.update(policy_id, enabled=True)

    async def disable(self, policy_id: str) -> Policy:
        """Async: Disable policy"""
        return await self.update(policy_id, enabled=False)
