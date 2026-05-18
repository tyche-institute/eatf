"""
Delegation API — matches backend DelegationChainController (/api/v1/delegation-chains).
"""

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .exceptions import NotFoundError
from .models import DelegationChain

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient

_DELEGATION_CHAINS = "/api/v1/delegation-chains"


def _iso_ts() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _coerce_chain_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Derive primaryAgentId / delegatedAgents / operatorId from nodes when API omits them."""
    out = dict(d)
    nodes = out.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return out
    ids: List[str] = []
    for n in nodes:
        if isinstance(n, dict) and n.get("id"):
            ids.append(str(n["id"]))
    if ids and not out.get("primaryAgentId") and not out.get("primary_agent_id"):
        out["primaryAgentId"] = ids[0]
        out["delegatedAgents"] = ids[1:]
    first = nodes[0]
    if isinstance(first, dict):
        meta = first.get("metadata")
        if isinstance(meta, dict):
            if meta.get("operatorId") and not out.get("operatorId") and not out.get("operator_id"):
                out["operatorId"] = meta.get("operatorId")
            if meta.get("policies") is not None and out.get("policies") is None:
                out["policies"] = meta.get("policies")
            if meta.get("sdkMetadata") is not None and out.get("metadata") is None:
                out["metadata"] = meta.get("sdkMetadata")
    return out


def _agent_in_chain(chain: DelegationChain, agent_id: str) -> bool:
    if chain.primary_agent_id == agent_id:
        return True
    if agent_id in chain.delegated_agents:
        return True
    for n in chain.nodes or []:
        if isinstance(n, dict) and str(n.get("id")) == agent_id:
            return True
    return False


def _chain_matches_filters(
    chain: DelegationChain,
    operator_id: Optional[str],
    agent_id: Optional[str],
    status: Optional[str],
) -> bool:
    if status and chain.status != status:
        return False
    if operator_id and chain.operator_id != operator_id:
        return False
    if agent_id and not _agent_in_chain(chain, agent_id):
        return False
    return True


def _build_visual_builder_payload(
    operator_id: str,
    primary_agent_id: str,
    delegated_agents: List[str],
    policies: Optional[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
    chain_name: str,
) -> List[Dict[str, Any]]:
    """Node list for POST /api/v1/delegation-chains (Visual Builder shape)."""
    ts = _iso_ts()
    root_meta: Dict[str, Any] = {
        "operatorId": operator_id,
        "sdkMetadata": metadata or {},
    }
    if policies is not None:
        root_meta["policies"] = policies
    nodes: List[Dict[str, Any]] = [
        {
            "id": primary_agent_id,
            "type": "operator",
            "name": primary_agent_id,
            "timestamp": ts,
            "metadata": root_meta,
        }
    ]
    prev = primary_agent_id
    for i, aid in enumerate(delegated_agents):
        nodes.append(
            {
                "id": aid,
                "type": "agent",
                "name": aid,
                "timestamp": ts,
                "metadata": {
                    "delegated_from": prev,
                    "delegation_level": i + 1,
                },
            }
        )
        prev = aid
    return nodes


class DelegationAPI:
    """Synchronous Delegation API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def create_chain(
        self,
        operator_id: str,
        primary_agent_id: str,
        delegated_agents: List[str],
        policies: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> DelegationChain:
        """
        Create a delegation chain via POST /api/v1/delegation-chains (Visual Builder payload).

        ``policies`` / ``metadata`` are stored under the primary node's ``metadata`` in ``nodes``.
        Optional kwargs: ``chain_name`` / ``name`` for the chain title.
        """
        max_depth = 5
        if policies and isinstance(policies.get("max_depth"), int):
            max_depth = policies["max_depth"]
        elif kwargs.get("max_depth") is not None:
            max_depth = int(kwargs["max_depth"])

        chain_name = (
            kwargs.get("chain_name")
            or kwargs.get("name")
            or f"SDK chain {primary_agent_id[:24]}..."
        )
        nodes = _build_visual_builder_payload(
            operator_id, primary_agent_id, delegated_agents, policies, kwargs.get("metadata"), chain_name
        )
        depth = len(delegated_agents)
        payload = {
            "name": chain_name,
            "nodes": nodes,
            "depth": depth,
            "maxDepth": max_depth,
        }

        data = self._client.request("POST", _DELEGATION_CHAINS, json=payload)
        now = datetime.now(UTC)
        return DelegationChain(
            chain_id=data["chainId"],
            name=data.get("name", chain_name),
            operator_id=operator_id,
            primary_agent_id=primary_agent_id,
            delegated_agents=list(delegated_agents),
            status=data.get("status", "active"),
            depth=depth,
            max_depth=max_depth,
            nodes=nodes,
            source="sdk",
            policies=policies,
            created_at=now,
            metadata=kwargs.get("metadata"),
            message=data.get("message"),
        )

    def get_chain(self, chain_id: str) -> DelegationChain:
        """Resolve by scanning GET /api/v1/delegation-chains (no GET-by-id route)."""
        for c in self.list_chains(limit=10_000):
            if c.chain_id == chain_id:
                return c
        raise NotFoundError(f"Delegation chain not found: {chain_id}", 404, None)

    def list_chains(
        self,
        operator_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DelegationChain]:
        """
        GET /api/v1/delegation-chains. Query params are not supported by the server;
        ``operator_id`` / ``agent_id`` / ``status`` are filtered client-side.
        """
        data = self._client.request("GET", _DELEGATION_CHAINS)
        raw_list = data if isinstance(data, list) else (data.get("chains") or data.get("items") or [])
        chains: List[DelegationChain] = []
        for raw in raw_list:
            if isinstance(raw, dict):
                chains.append(DelegationChain.model_validate(_coerce_chain_dict(raw)))
        filtered = [c for c in chains if _chain_matches_filters(c, operator_id, agent_id, status)]
        return filtered[offset : offset + limit]

    def verify_chain(self, chain_id: str) -> bool:
        """No verify endpoint — returns True if the chain appears in the tenant list."""
        try:
            self.get_chain(chain_id)
            return True
        except NotFoundError:
            return False

    def revoke_chain(self, chain_id: str, reason: Optional[str] = None) -> DelegationChain:
        _ = reason
        raise NotImplementedError("Delegation chain revocation is not exposed by the API.")

    def get_agent_delegations(self, agent_id: str) -> List[DelegationChain]:
        """Filter chains from GET /api/v1/delegation-chains where ``agent_id`` appears."""
        return [c for c in self.list_chains(limit=10_000) if _agent_in_chain(c, agent_id)]


class AsyncDelegationAPI:
    """Asynchronous Delegation API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def create_chain(
        self,
        operator_id: str,
        primary_agent_id: str,
        delegated_agents: List[str],
        policies: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> DelegationChain:
        max_depth = 5
        if policies and isinstance(policies.get("max_depth"), int):
            max_depth = policies["max_depth"]
        elif kwargs.get("max_depth") is not None:
            max_depth = int(kwargs["max_depth"])

        chain_name = (
            kwargs.get("chain_name")
            or kwargs.get("name")
            or f"SDK chain {primary_agent_id[:24]}..."
        )
        nodes = _build_visual_builder_payload(
            operator_id, primary_agent_id, delegated_agents, policies, kwargs.get("metadata"), chain_name
        )
        depth = len(delegated_agents)
        payload = {
            "name": chain_name,
            "nodes": nodes,
            "depth": depth,
            "maxDepth": max_depth,
        }

        data = await self._client.request("POST", _DELEGATION_CHAINS, json=payload)
        now = datetime.now(UTC)
        return DelegationChain(
            chain_id=data["chainId"],
            name=data.get("name", chain_name),
            operator_id=operator_id,
            primary_agent_id=primary_agent_id,
            delegated_agents=list(delegated_agents),
            status=data.get("status", "active"),
            depth=depth,
            max_depth=max_depth,
            nodes=nodes,
            source="sdk",
            policies=policies,
            created_at=now,
            metadata=kwargs.get("metadata"),
            message=data.get("message"),
        )

    async def get_chain(self, chain_id: str) -> DelegationChain:
        for c in await self.list_chains(limit=10_000):
            if c.chain_id == chain_id:
                return c
        raise NotFoundError(f"Delegation chain not found: {chain_id}", 404, None)

    async def list_chains(
        self,
        operator_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DelegationChain]:
        data = await self._client.request("GET", _DELEGATION_CHAINS)
        raw_list = data if isinstance(data, list) else (data.get("chains") or data.get("items") or [])
        chains: List[DelegationChain] = []
        for raw in raw_list:
            if isinstance(raw, dict):
                chains.append(DelegationChain.model_validate(_coerce_chain_dict(raw)))
        filtered = [c for c in chains if _chain_matches_filters(c, operator_id, agent_id, status)]
        return filtered[offset : offset + limit]

    async def verify_chain(self, chain_id: str) -> bool:
        try:
            await self.get_chain(chain_id)
            return True
        except NotFoundError:
            return False

    async def revoke_chain(self, chain_id: str, reason: Optional[str] = None) -> DelegationChain:
        _ = chain_id, reason
        raise NotImplementedError("Delegation chain revocation is not exposed by the API.")

    async def get_agent_delegations(self, agent_id: str) -> List[DelegationChain]:
        all_c = await self.list_chains(limit=10_000)
        return [c for c in all_c if _agent_in_chain(c, agent_id)]
