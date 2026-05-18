"""
Main Aletheia API Client
"""

import asyncio
import time
from typing import Optional, Dict, Any
import httpx
from .config import Config
from .exceptions import (
    AletheiaAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
    TimeoutError as AletheiaTimeoutError,
)

# HTTP status codes that are safe to retry (transient infra failures, not
# client errors). 429 is handled separately via RateLimitError and Retry-After.
_RETRYABLE_STATUS = {502, 503, 504}
from .models import LoginRequest, AuthResponse
from .agents import AgentsAPI, AsyncAgentsAPI
from .audit import AuditAPI, AsyncAuditAPI
from .policies import PoliciesAPI, AsyncPoliciesAPI
from .verification import VerificationAPI, AsyncVerificationAPI
from .delegation import DelegationAPI, AsyncDelegationAPI
from .compliance import ComplianceAPI, AsyncComplianceAPI
from .actions import ActionsAPI
from .attestations import AttestationsAPI, AsyncAttestationsAPI
from .evidence import EvidenceAPI


class BaseClient:
    """Base client with common HTTP handling"""

    def __init__(self, config: Config):
        self.config = config
        self._token: Optional[str] = config.token
        self._session: Optional[httpx.Client] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if self.config.tenant_id:
            headers["X-Tenant-Id"] = str(self.config.tenant_id).strip()
        elif self.config.organization:
            org = str(self.config.organization).strip()
            if org.isdigit():
                headers["X-Tenant-Id"] = org
            else:
                headers["X-Tenant-Key"] = org
        return headers

    def _handle_error(self, response: httpx.Response):
        """Handle HTTP error responses"""
        error_data = None
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                message = error_data.get("message", response.text)
            else:
                message = response.text or f"HTTP {response.status_code}"
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 401:
            raise AuthenticationError(message, response.status_code, error_data)
        elif response.status_code == 403:
            raise AuthorizationError(message, response.status_code, error_data)
        elif response.status_code == 404:
            raise NotFoundError(message, response.status_code, error_data)
        elif response.status_code == 400:
            details = (
                error_data.get("details")
                if isinstance(error_data, dict)
                else None
            )
            raise ValidationError(
                message,
                response.status_code,
                error_data,
                details,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message,
                response.status_code,
                error_data,
                int(retry_after) if retry_after else None,
            )
        elif response.status_code >= 500:
            raise ServerError(message, response.status_code, error_data)
        else:
            raise AletheiaAPIError(message, response.status_code, error_data)


class AletheiaClient(BaseClient):
    """
    Synchronous Aletheia API Client
    
    Example:
        ```python
        client = AletheiaClient(
            base_url="https://api.aletheia.ai",
            email="user@example.com",
            password="secret"
        )
        
        # Register agent
        agent = client.agents.create(
            name="My Agent",
            agent_type="CONVERSATIONAL"
        )
        
        # Log event
        event = client.audit.log_event(
            agent_id=agent.agent_id,
            event_type="COMPLIANCE_CHECK_PASSED",
            action="predict",
            outcome="SUCCESS"
        )
        ```
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        organization: Optional[str] = None,
        config: Optional[Config] = None,
        auto_login: bool = False,
    ):
        """
        Initialize Aletheia client

        Args:
            base_url: API endpoint URL
            email: User email for authentication
            password: User password for authentication
            token: JWT token (alternative to email/password)
            organization: Organization/tenant identifier
            config: Complete configuration object (overrides other params)
            auto_login: If True and email/password are provided, call
                ``login()`` during initialization. Defaults to False so that
                constructing a client never performs network I/O; call
                ``client.login(...)`` explicitly when you want to authenticate.
        """
        if config is None:
            config = Config(
                base_url=base_url or Config().base_url,
                email=email,
                password=password,
                token=token,
                organization=organization,
            )

        super().__init__(config)

        # Initialize session
        self._session = httpx.Client(
            timeout=config.timeout,
            verify=config.verify_ssl,
        )

        # Initialize API modules
        self.agents = AgentsAPI(self)
        self.audit = AuditAPI(self)
        self.policies = PoliciesAPI(self)
        self.verification = VerificationAPI(self)
        self.delegation = DelegationAPI(self)
        self.compliance = ComplianceAPI(self)
        self.actions = ActionsAPI(self)
        self.attestations = AttestationsAPI(self)
        # Offline .aep verification — no network, no API key needed.
        # cryptography is an optional [verify] dep; lazy-loaded inside the call.
        self.evidence = EvidenceAPI()  # noqa: PIE794 — sync client variant

        if auto_login and not self._token and config.email and config.password:
            self.login(config.email, config.password, config.organization)

    def login(
        self, email: str, password: str, organization: Optional[str] = None
    ) -> AuthResponse:
        """
        Authenticate with email and password
        
        Args:
            email: User email
            password: User password
            organization: Optional organization identifier
            
        Returns:
            AuthResponse with token and user info
        """
        request = LoginRequest(
            email=email, password=password, tenant_key=organization
        )
        response = self._session.post(
            f"{self.config.base_url}/api/auth/credentials",
            json=request.model_dump(by_alias=True, exclude_none=True),
            headers={"Content-Type": "application/json"},
        )

        if not response.is_success:
            self._handle_error(response)

        data = response.json()
        auth = AuthResponse(**data)
        self._token = auth.access_token

        self.config.organization = auth.tenant_key

        return auth

    def request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (without base URL)
            json: JSON request body
            params: Query parameters

        Returns:
            Response data as dictionary
        """
        if not self._session:
            raise AletheiaAPIError("Client not initialized")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        attempts = max(1, self.config.max_retries + 1)
        last_exc: Optional[Exception] = None
        for attempt in range(attempts):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )

                if response.status_code in _RETRYABLE_STATUS and attempt < attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue

                if not response.is_success:
                    self._handle_error(response)

                # Return empty dict for 204 No Content
                if response.status_code == 204:
                    return {}

                return response.json()

            except httpx.TimeoutException as e:
                last_exc = AletheiaTimeoutError(f"Request timed out: {e}")
            except httpx.NetworkError as e:
                last_exc = NetworkError(f"Network error: {e}")

            if attempt < attempts - 1:
                time.sleep(self.config.retry_delay * (2 ** attempt))

        assert last_exc is not None
        raise last_exc

    def request_with_status(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> tuple[Dict[str, Any], int]:
        """Variant of :meth:`request` that returns ``(data, status_code)``.

        Lets callers distinguish 201 Created from 200 OK on idempotent endpoints
        like ``PUT /api/v1/agents/{agentId}`` (RFC #72). Retry / auth / error
        semantics are identical to :meth:`request`.
        """
        if not self._session:
            raise AletheiaAPIError("Client not initialized")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        attempts = max(1, self.config.max_retries + 1)
        last_exc: Optional[Exception] = None
        for attempt in range(attempts):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )

                if response.status_code in _RETRYABLE_STATUS and attempt < attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue

                if not response.is_success:
                    self._handle_error(response)

                if response.status_code == 204:
                    return {}, 204

                return response.json(), response.status_code

            except httpx.TimeoutException as e:
                last_exc = AletheiaTimeoutError(f"Request timed out: {e}")
            except httpx.NetworkError as e:
                last_exc = NetworkError(f"Network error: {e}")

            if attempt < attempts - 1:
                time.sleep(self.config.retry_delay * (2 ** attempt))

        assert last_exc is not None
        raise last_exc

    def download(self, path: str) -> bytes:
        """
        Download binary content
        
        Args:
            path: API path
            
        Returns:
            Binary content
        """
        if not self._session:
            raise AletheiaAPIError("Client not initialized")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        try:
            response = self._session.get(url, headers=headers)

            if not response.is_success:
                self._handle_error(response)

            return response.content

        except httpx.TimeoutException as e:
            raise AletheiaTimeoutError(f"Request timed out: {e}")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")

    def close(self):
        """Close HTTP session"""
        if self._session:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def from_config(cls, config: Config) -> "AletheiaClient":
        """Create client from Config object"""
        return cls(config=config)


class AsyncAletheiaClient(BaseClient):
    """
    Async Aletheia API Client
    
    Example:
        ```python
        async with AsyncAletheiaClient(
            base_url="https://api.aletheia.ai",
            email="user@example.com",
            password="secret"
        ) as client:
            agent = await client.agents.create(
                name="My Agent",
                agent_type="CONVERSATIONAL"
            )
        ```
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        organization: Optional[str] = None,
        config: Optional[Config] = None,
        auto_login: bool = False,
    ):
        if config is None:
            config = Config(
                base_url=base_url or Config().base_url,
                email=email,
                password=password,
                token=token,
                organization=organization,
            )

        super().__init__(config)

        self._async_session: Optional[httpx.AsyncClient] = None
        self._auto_login = auto_login

        # Initialize async API modules
        self.agents = AsyncAgentsAPI(self)
        self.audit = AsyncAuditAPI(self)
        self.policies = AsyncPoliciesAPI(self)
        self.verification = AsyncVerificationAPI(self)
        self.delegation = AsyncDelegationAPI(self)
        self.compliance = AsyncComplianceAPI(self)
        self.attestations = AsyncAttestationsAPI(self)
        # Offline .aep verification is sync (no I/O beyond the local file +
        # local crypto). Same instance shape on both clients so symmetric
        # partner code keeps working.
        self.evidence = EvidenceAPI()

    async def __aenter__(self):
        self._async_session = httpx.AsyncClient(
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

        if (
            self._auto_login
            and not self._token
            and self.config.email
            and self.config.password
        ):
            await self.login(
                self.config.email, self.config.password, self.config.organization
            )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def login(
        self, email: str, password: str, organization: Optional[str] = None
    ) -> AuthResponse:
        """Async authentication"""
        if not self._async_session:
            raise AletheiaAPIError("Client not initialized")

        request = LoginRequest(
            email=email, password=password, tenant_key=organization
        )
        response = await self._async_session.post(
            f"{self.config.base_url}/api/auth/credentials",
            json=request.model_dump(by_alias=True, exclude_none=True),
            headers={"Content-Type": "application/json"},
        )

        if not response.is_success:
            self._handle_error(response)

        data = response.json()
        auth = AuthResponse(**data)
        self._token = auth.access_token

        self.config.organization = auth.tenant_key

        return auth

    async def request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async HTTP request"""
        if not self._async_session:
            raise AletheiaAPIError("Client not initialized. Use 'async with' context.")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        attempts = max(1, self.config.max_retries + 1)
        last_exc: Optional[Exception] = None
        for attempt in range(attempts):
            try:
                response = await self._async_session.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )

                if response.status_code in _RETRYABLE_STATUS and attempt < attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue

                if not response.is_success:
                    self._handle_error(response)

                if response.status_code == 204:
                    return {}

                return response.json()

            except httpx.TimeoutException as e:
                last_exc = AletheiaTimeoutError(f"Request timed out: {e}")
            except httpx.NetworkError as e:
                last_exc = NetworkError(f"Network error: {e}")

            if attempt < attempts - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

        assert last_exc is not None
        raise last_exc

    async def request_with_status(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> tuple[Dict[str, Any], int]:
        """Async variant of :meth:`request_with_status`."""
        if not self._async_session:
            raise AletheiaAPIError("Client not initialized. Use 'async with' context.")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        attempts = max(1, self.config.max_retries + 1)
        last_exc: Optional[Exception] = None
        for attempt in range(attempts):
            try:
                response = await self._async_session.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=headers,
                )

                if response.status_code in _RETRYABLE_STATUS and attempt < attempts - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                    continue

                if not response.is_success:
                    self._handle_error(response)

                if response.status_code == 204:
                    return {}, 204

                return response.json(), response.status_code

            except httpx.TimeoutException as e:
                last_exc = AletheiaTimeoutError(f"Request timed out: {e}")
            except httpx.NetworkError as e:
                last_exc = NetworkError(f"Network error: {e}")

            if attempt < attempts - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

        assert last_exc is not None
        raise last_exc

    async def download(self, path: str) -> bytes:
        """Async download binary content"""
        if not self._async_session:
            raise AletheiaAPIError("Client not initialized")

        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        try:
            response = await self._async_session.get(url, headers=headers)

            if not response.is_success:
                self._handle_error(response)

            return response.content

        except httpx.TimeoutException as e:
            raise AletheiaTimeoutError(f"Request timed out: {e}")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")

    async def close(self):
        """Close async session"""
        if self._async_session:
            await self._async_session.aclose()

    @classmethod
    def from_config(cls, config: Config) -> "AsyncAletheiaClient":
        """Create async client from Config object"""
        return cls(config=config)
