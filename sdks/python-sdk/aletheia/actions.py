"""
Agent action requests (partner governance gate: human approve/deny + audit).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from aletheia.client import AletheiaClient


class ActionRequest(BaseModel):
    request_id: str = Field(alias="requestId")
    agent_id: str = Field(alias="agentId")
    action_type: str = Field(alias="actionType")
    status: str
    correlation_id: Optional[str] = Field(None, alias="correlationId")
    payload_json: Optional[str] = Field(None, alias="payloadJson")
    requested_by: Optional[str] = Field(None, alias="requestedBy")
    decided_by: Optional[str] = Field(None, alias="decidedBy")
    decision_comment: Optional[str] = Field(None, alias="decisionComment")
    created_at: Optional[str] = Field(None, alias="createdAt")
    decided_at: Optional[str] = Field(None, alias="decidedAt")
    create_audit_event_id: Optional[int] = Field(None, alias="createAuditEventId")
    decision_audit_event_id: Optional[int] = Field(None, alias="decisionAuditEventId")

    model_config = ConfigDict(populate_by_name=True)


class ActionsAPI:
    def __init__(self, client: AletheiaClient):
        self._client = client

    def create_request(
        self,
        agent_id: str,
        action_type: str,
        payload: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        requested_by: Optional[str] = None,
    ) -> ActionRequest:
        body: Dict[str, Any] = {
            "agentId": agent_id,
            "actionType": action_type,
        }
        if payload is not None:
            body["payload"] = payload
        if correlation_id:
            body["correlationId"] = correlation_id
        if requested_by:
            body["requestedBy"] = requested_by
        r = self._client._session.post(
            f"{self._client.config.base_url}/api/v1/action-requests",
            json=body,
            headers=self._client._get_headers(),
        )
        if not r.is_success:
            self._client._handle_error(r)
        return ActionRequest.model_validate(r.json())

    def get(self, request_id: str) -> ActionRequest:
        r = self._client._session.get(
            f"{self._client.config.base_url}/api/v1/action-requests/{request_id}",
            headers=self._client._get_headers(),
        )
        if not r.is_success:
            self._client._handle_error(r)
        return ActionRequest.model_validate(r.json())

    def list_for_agent(
        self, agent_id: str, status: Optional[str] = None
    ) -> List[ActionRequest]:
        params: Dict[str, str] = {"agentId": agent_id}
        if status:
            params["status"] = status
        r = self._client._session.get(
            f"{self._client.config.base_url}/api/v1/action-requests",
            params=params,
            headers=self._client._get_headers(),
        )
        if not r.is_success:
            self._client._handle_error(r)
        return [ActionRequest.model_validate(x) for x in r.json()]

    def approve(
        self,
        request_id: str,
        comment: Optional[str] = None,
        decided_by: Optional[str] = None,
    ) -> ActionRequest:
        body: Dict[str, Any] = {}
        if comment is not None:
            body["comment"] = comment
        if decided_by is not None:
            body["decidedBy"] = decided_by
        r = self._client._session.post(
            f"{self._client.config.base_url}/api/v1/action-requests/{request_id}/approve",
            json=body if body else {},
            headers=self._client._get_headers(),
        )
        if not r.is_success:
            self._client._handle_error(r)
        return ActionRequest.model_validate(r.json())

    def deny(
        self,
        request_id: str,
        comment: Optional[str] = None,
        decided_by: Optional[str] = None,
    ) -> ActionRequest:
        body: Dict[str, Any] = {}
        if comment is not None:
            body["comment"] = comment
        if decided_by is not None:
            body["decidedBy"] = decided_by
        r = self._client._session.post(
            f"{self._client.config.base_url}/api/v1/action-requests/{request_id}/deny",
            json=body if body else {},
            headers=self._client._get_headers(),
        )
        if not r.is_success:
            self._client._handle_error(r)
        return ActionRequest.model_validate(r.json())
