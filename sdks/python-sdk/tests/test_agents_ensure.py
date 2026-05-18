"""Tests for AgentsAPI.ensure() — RFC #72 manifest-pattern upsert."""

from unittest.mock import MagicMock

import httpx
import pytest

from aletheia import (
    AgentTenantConflictError,
    AletheiaAPIError,
    AletheiaClient,
    Config,
    EnsureResult,
)


def _make_client():
    return AletheiaClient(
        base_url="https://api.example.com",
        token="test-token",
        config=Config(
            base_url="https://api.example.com",
            token="test-token",
            max_retries=0,
            retry_delay=0.0,
        ),
    )


def _agent_response_payload():
    """Shape returned by the server's AgentResponse DTO."""
    return {
        "agentId": "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
        "name": "EU AI Act Advisor",
        "agentType": "custom",
        "riskClassification": "high",
        "status": "active",
        "trustScore": 90,
    }


def _mock_response(status_code: int, payload):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = payload
    response.text = "" if isinstance(payload, dict) else str(payload)
    response.headers = {}
    return response


def test_ensure_returns_created_true_on_201():
    client = _make_client()
    client._session = MagicMock()
    client._session.request.return_value = _mock_response(201, _agent_response_payload())

    result = client.agents.ensure(
        "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
        display_name="EU AI Act Advisor",
        agent_type="custom",
        risk_classification="high",
        capabilities=["regulatory-qa"],
        eidas_level="qualified",
    )

    assert isinstance(result, EnsureResult)
    assert result.created is True
    assert result.agent.agent_id == "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee"

    # Verify the request shape sent to the server
    args, kwargs = client._session.request.call_args
    assert kwargs["method"] == "PUT"
    assert kwargs["url"].endswith("/api/v1/agents/urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee")
    body = kwargs["json"]
    # agentId belongs in URL, not body
    assert "agentId" not in body
    assert body["name"] == "EU AI Act Advisor"
    assert body["agentType"] == "custom"
    assert body["riskClassification"] == "high"
    assert body["capabilities"] == ["regulatory-qa"]
    assert body["eidasLevel"] == "qualified"


def test_ensure_returns_created_false_on_200():
    client = _make_client()
    client._session = MagicMock()
    client._session.request.return_value = _mock_response(200, _agent_response_payload())

    result = client.agents.ensure(
        "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
        display_name="EU AI Act Advisor",
        agent_type="custom",
        risk_classification="high",
    )

    assert result.created is False
    assert result.agent.agent_id == "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee"


def test_ensure_raises_tenant_conflict_on_409():
    client = _make_client()
    conflict_payload = {
        "code": "AGENT_ID_CONFLICT",
        "message": "agentId already in use on a different tenant",
    }
    response = _mock_response(409, conflict_payload)
    response.text = '{"code":"AGENT_ID_CONFLICT","message":"agentId already in use on a different tenant"}'
    client._session = MagicMock()
    client._session.request.return_value = response

    with pytest.raises(AgentTenantConflictError) as ei:
        client.agents.ensure(
            "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
            display_name="EU AI Act Advisor",
            agent_type="custom",
            risk_classification="high",
        )
    err = ei.value
    assert err.status_code == 409
    assert err.agent_id == "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee"
    # The error message must NOT include any tenant identifier
    assert "tenant_id" not in str(err)
    assert "tenantId" not in str(err)


def test_ensure_passes_through_validation_error_on_400():
    client = _make_client()
    bad = _mock_response(400, {"message": "agentId must be 255 characters or fewer"})
    bad.text = '{"message":"agentId must be 255 characters or fewer"}'
    client._session = MagicMock()
    client._session.request.return_value = bad

    with pytest.raises(AletheiaAPIError) as ei:
        client.agents.ensure(
            "x" * 256,
            display_name="EU AI Act Advisor",
            agent_type="custom",
            risk_classification="high",
        )
    assert ei.value.status_code == 400
    # Should NOT be the conflict subclass
    assert not isinstance(ei.value, AgentTenantConflictError)


def test_ensure_omits_unspecified_optional_fields():
    """exclude_none=True keeps the wire payload minimal so the server's
    applyMutableFields leaves untouched fields alone on update."""
    client = _make_client()
    client._session = MagicMock()
    client._session.request.return_value = _mock_response(200, _agent_response_payload())

    client.agents.ensure(
        "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
        display_name="EU AI Act Advisor",
        agent_type="custom",
        risk_classification="high",
    )

    body = client._session.request.call_args.kwargs["json"]
    # Optional unset fields should not appear
    for absent in (
        "description",
        "organization",
        "contactEmail",
        "capabilities",
        "eidasCertificateArn",
        "eidasLevel",
        "signatureAlgorithm",
        "primaryJurisdiction",
        "transactionLimit",
        "transactionCurrency",
        "mcpDid",
    ):
        assert absent not in body, f"unexpected field in body: {absent}"


def test_ensure_url_keeps_full_urn():
    """The agentId in the URL keeps colons and dashes intact (not a query
    parameter, not an opaque token); httpx will percent-encode at send time
    if the URL parser deems it necessary, but we don't pre-encode."""
    client = _make_client()
    client._session = MagicMock()
    client._session.request.return_value = _mock_response(201, _agent_response_payload())

    client.agents.ensure(
        "urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee",
        display_name="EU AI Act Advisor",
        agent_type="custom",
        risk_classification="high",
    )

    url = client._session.request.call_args.kwargs["url"]
    assert url == "https://api.example.com/api/v1/agents/urn:uuid:d11c3f17-85dd-4e46-908f-6d5cf9df79ee"


def test_ensure_namespaced_slug_round_trips():
    client = _make_client()
    client._session = MagicMock()
    payload = _agent_response_payload()
    payload["agentId"] = "eatf-demo:eu-ai-act-agent"
    client._session.request.return_value = _mock_response(201, payload)

    result = client.agents.ensure(
        "eatf-demo:eu-ai-act-agent",
        display_name="EU AI Act Advisor",
        agent_type="custom",
        risk_classification="high",
    )

    assert result.agent.agent_id == "eatf-demo:eu-ai-act-agent"
    url = client._session.request.call_args.kwargs["url"]
    assert url.endswith("/api/v1/agents/eatf-demo:eu-ai-act-agent")
