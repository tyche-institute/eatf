"""
Basic tests for Aletheia SDK
"""

import asyncio
from unittest.mock import MagicMock

import httpx
import pytest
from aletheia import AletheiaClient, Config
from aletheia.exceptions import (
    AletheiaAPIError,
    AuthenticationError,
    NetworkError,
    ServerError,
    TimeoutError as AletheiaTimeoutError,
)


def test_config_creation():
    """Test Config object creation"""
    config = Config(
        base_url="https://api.example.com",
        email="test@example.com",
        timeout=60.0
    )
    
    assert config.base_url == "https://api.example.com"
    assert config.email == "test@example.com"
    assert config.timeout == 60.0
    assert config.max_retries == 3


def test_config_strips_trailing_slash():
    """Test that trailing slash is removed from base_url"""
    config = Config(base_url="https://api.example.com/")
    assert config.base_url == "https://api.example.com"


def test_client_initialization():
    """Test client initialization"""
    client = AletheiaClient(
        base_url="https://api.example.com",
        email="test@example.com",
        password="password123"
    )
    
    assert client.config.base_url == "https://api.example.com"
    assert client.config.email == "test@example.com"


def test_client_from_config():
    """Test client creation from Config object"""
    config = Config(
        base_url="https://api.example.com",
        email="test@example.com",
        password="password123"
    )
    
    client = AletheiaClient.from_config(config)
    assert client.config == config


def test_client_context_manager():
    """Test client context manager"""
    with AletheiaClient(
        base_url="https://api.example.com",
        token="test-token"
    ) as client:
        assert client._session is not None
    
    # Session should be closed after context exit
    assert client._session is not None  # Still exists, just closed


def test_async_client_context_manager():
    """Test async client context manager without pytest-asyncio dependency."""
    from aletheia import AsyncAletheiaClient

    async def run():
        async with AsyncAletheiaClient(
            base_url="https://api.example.com",
            token="test-token"
        ) as client:
            assert client._async_session is not None

    asyncio.run(run())


def test_get_headers():
    """Test header generation"""
    client = AletheiaClient(
        base_url="https://api.example.com",
        token="test-token-123",
        organization="test-org"
    )
    
    headers = client._get_headers()
    
    assert headers["Authorization"] == "Bearer test-token-123"
    assert headers["X-Tenant-Key"] == "test-org"
    assert headers["Content-Type"] == "application/json"


def test_config_to_dict():
    """Test config serialization (excluding sensitive data)"""
    config = Config(
        base_url="https://api.example.com",
        email="test@example.com",
        password="secret123",  # Should NOT appear in dict
        token="secret-token",   # Should NOT appear in dict
        organization="test-org",
        timeout=30.0
    )
    
    config_dict = config.to_dict()
    
    assert config_dict["base_url"] == "https://api.example.com"
    assert config_dict["organization"] == "test-org"
    assert config_dict["timeout"] == 30.0
    assert "password" not in config_dict
    assert "token" not in config_dict
    assert "email" not in config_dict


def _make_client(max_retries: int = 2):
    client = AletheiaClient(
        base_url="https://api.example.com",
        token="test-token",
        config=Config(
            base_url="https://api.example.com",
            token="test-token",
            max_retries=max_retries,
            retry_delay=0.0,
        ),
    )
    return client


def test_request_retries_on_timeout_then_succeeds():
    client = _make_client(max_retries=2)
    ok = MagicMock(spec=httpx.Response)
    ok.status_code = 200
    ok.is_success = True
    ok.json.return_value = {"ok": True}

    client._session = MagicMock()
    client._session.request.side_effect = [
        httpx.ReadTimeout("stream idle timeout"),
        ok,
    ]

    assert client.request("GET", "/x") == {"ok": True}
    assert client._session.request.call_count == 2


def test_request_retries_on_5xx_then_succeeds():
    client = _make_client(max_retries=2)
    bad = MagicMock(spec=httpx.Response)
    bad.status_code = 503
    bad.is_success = False
    ok = MagicMock(spec=httpx.Response)
    ok.status_code = 200
    ok.is_success = True
    ok.json.return_value = {"ok": True}

    client._session = MagicMock()
    client._session.request.side_effect = [bad, ok]

    assert client.request("GET", "/x") == {"ok": True}
    assert client._session.request.call_count == 2


def test_request_raises_timeout_after_exhausting_retries():
    client = _make_client(max_retries=1)
    client._session = MagicMock()
    client._session.request.side_effect = httpx.ReadTimeout("boom")

    with pytest.raises(AletheiaTimeoutError):
        client.request("GET", "/x")
    # max_retries=1 => 2 total attempts
    assert client._session.request.call_count == 2


def test_request_does_not_retry_on_4xx():
    client = _make_client(max_retries=3)
    bad = MagicMock(spec=httpx.Response)
    bad.status_code = 400
    bad.is_success = False
    bad.text = '{"message":"bad"}'
    bad.json.return_value = {"message": "bad"}

    client._session = MagicMock()
    client._session.request.return_value = bad

    with pytest.raises(AletheiaAPIError):
        client.request("GET", "/x")
    assert client._session.request.call_count == 1
