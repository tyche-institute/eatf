"""
Configuration management for Aletheia SDK
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class Config:
    """Configuration for Aletheia API client"""

    # API endpoint
    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "ALETHEIA_API_URL", "http://localhost:8080"
        )
    )

    # Authentication
    email: Optional[str] = field(
        default_factory=lambda: os.environ.get("ALETHEIA_EMAIL")
    )
    password: Optional[str] = field(
        default_factory=lambda: os.environ.get("ALETHEIA_PASSWORD")
    )
    # A pre-minted credential used directly as `Authorization: Bearer <token>`.
    # Accepts either a short-lived JWT from /api/auth/credentials (ALETHEIA_TOKEN)
    # or a long-lived partner API key minted in the developer portal (ALETHEIA_API_KEY).
    # ALETHEIA_API_KEY wins if both are set.
    token: Optional[str] = field(
        default_factory=lambda: os.environ.get("ALETHEIA_API_KEY")
        or os.environ.get("ALETHEIA_TOKEN")
    )

    # Tenant/Organization
    organization: Optional[str] = field(
        default_factory=lambda: os.environ.get("ALETHEIA_ORGANIZATION")
    )
    tenant_id: Optional[str] = field(
        default_factory=lambda: os.environ.get("ALETHEIA_TENANT_ID")
    )

    # HTTP settings
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True

    # Logging
    log_level: str = "INFO"
    debug: bool = False

    def __post_init__(self):
        """Validate configuration"""
        if not self.base_url:
            raise ValueError("base_url is required")

        # Remove trailing slash from base_url
        self.base_url = self.base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables"""
        return cls()

    def to_dict(self):
        """Convert config to dictionary (excluding sensitive data)"""
        return {
            "base_url": self.base_url,
            "organization": self.organization,
            "tenant_id": self.tenant_id,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
        }
