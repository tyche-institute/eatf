"""
Aletheia SDK Exception Classes
"""

from typing import Any, Dict, Optional


class AletheiaAPIError(Exception):
    """Base exception for all Aletheia API errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(AletheiaAPIError):
    """Raised when authentication fails (401)"""

    pass


class AuthorizationError(AletheiaAPIError):
    """Raised when user lacks permission (403)"""

    pass


class NotFoundError(AletheiaAPIError):
    """Raised when resource is not found (404)"""

    pass


class ValidationError(AletheiaAPIError):
    """Raised when request validation fails (400)"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, response)
        self.details = details or {}


class RateLimitError(AletheiaAPIError):
    """Raised when rate limit is exceeded (429)"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code, response)
        self.retry_after = retry_after


class ServerError(AletheiaAPIError):
    """Raised when server encounters an error (5xx)"""

    pass


class NetworkError(AletheiaAPIError):
    """Raised when network request fails"""

    pass


class TimeoutError(AletheiaAPIError):
    """Raised when request times out"""

    pass


class AgentTenantConflictError(AletheiaAPIError):
    """Raised when ``agents.ensure()`` finds the requested ``agent_id`` already
    bound to a different tenant. Maps to HTTP 409 ``AGENT_ID_CONFLICT`` from
    ``PUT /api/v1/agents/{agent_id}`` (RFC #72). The error message and the
    parsed response deliberately do not name the owning tenant.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
    ):
        super().__init__(message, status_code, response)
        self.agent_id = agent_id
