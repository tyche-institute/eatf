"""
Pydantic models for Aletheia API
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Authentication Models
# ============================================================================


class LoginRequest(BaseModel):
    """POST /api/auth/credentials body (camelCase on the wire)."""

    model_config = ConfigDict(populate_by_name=True)

    email: str
    password: str
    tenant_key: Optional[str] = Field(None, alias="tenantKey")


class AuthResponse(BaseModel):
    """Response from POST /api/auth/credentials."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    access_token: str = Field(..., alias="accessToken")
    user_id: int = Field(..., alias="userId")
    tenant_id: int = Field(..., alias="tenantId")
    tenant_key: str = Field(..., alias="tenantKey")
    tenant_name: Optional[str] = Field(None, alias="tenantName")
    role: str
    email: str
    name: Optional[str] = None


# ============================================================================
# Agent Models
# ============================================================================


class AgentCreate(BaseModel):
    """Agent registration body for POST /api/v1/agents/register."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    agent_type: str = Field(
        ...,
        alias="agentType",
        description="CONVERSATIONAL, ANALYTICAL, ROBOTIC, etc.",
    )
    risk_classification: str = Field(
        ...,
        alias="riskClassification",
        description="minimal, limited, high",
    )
    capabilities: List[str] = Field(default_factory=list)
    primary_jurisdiction: str = Field("EU", alias="primaryJurisdiction")
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Agent(BaseModel):
    """Agent response (matches AgentResponse; extra fields ignored)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    agent_id: str = Field(..., alias="agentId")
    name: str
    agent_type: str = Field(..., alias="agentType")
    status: Optional[str] = None
    risk_classification: Optional[str] = Field(None, alias="riskClassification")
    capabilities: Any = Field(default_factory=list)
    primary_jurisdiction: Optional[str] = Field(None, alias="primaryJurisdiction")
    description: Optional[str] = None
    organization: Optional[str] = None
    contact_email: Optional[str] = Field(None, alias="contactEmail")
    registered_at: Optional[datetime] = Field(None, alias="registeredAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    metadata: Optional[Dict[str, Any]] = None
    trust_score: Optional[int] = Field(None, alias="trustScore")


class AgentUpdate(BaseModel):
    """Agent update request"""

    name: Optional[str] = None
    status: Optional[str] = None
    risk_classification: Optional[str] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentEnsureRequest(BaseModel):
    """Body for ``PUT /api/v1/agents/{agentId}`` (RFC #72 manifest upsert).

    Caller-supplied ``agent_id`` belongs in the URL path, not the body — see
    :meth:`aletheia.agents.AgentsAPI.ensure`. Mirrors the Java
    ``AgentRegistrationRequest`` record on the server.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: Optional[str] = None
    organization: Optional[str] = None
    contact_email: Optional[str] = Field(None, alias="contactEmail")
    agent_type: str = Field(..., alias="agentType")
    risk_classification: str = Field(..., alias="riskClassification")
    capabilities: Optional[List[str]] = None
    eidas_certificate_arn: Optional[str] = Field(None, alias="eidasCertificateArn")
    eidas_level: Optional[str] = Field(None, alias="eidasLevel")
    signature_algorithm: Optional[str] = Field(None, alias="signatureAlgorithm")
    primary_jurisdiction: Optional[str] = Field(None, alias="primaryJurisdiction")
    transaction_limit: Optional[float] = Field(None, alias="transactionLimit")
    transaction_currency: Optional[str] = Field(None, alias="transactionCurrency")
    mcp_did: Optional[str] = Field(None, alias="mcpDid")


class EnsureResult(BaseModel):
    """Outcome of ``agents.ensure()`` (RFC #72 manifest pattern).

    ``created`` is True when the PUT inserted a new row (HTTP 201) and False
    when an existing row was patched in place (HTTP 200). The HTTP layer
    translates 409 into :class:`aletheia.exceptions.AgentTenantConflictError`,
    so an EnsureResult always represents a successful upsert on the caller's
    own tenant.
    """

    model_config = ConfigDict(populate_by_name=True)

    agent: "Agent"
    created: bool


# ============================================================================
# Audit Models
# ============================================================================


class AuditEventCreate(BaseModel):
    """Audit event creation request"""

    model_config = ConfigDict(populate_by_name=True)

    agent_id: str = Field(..., alias="agentId")
    event_type: str = Field(..., alias="eventType")
    action: str
    resource: Optional[str] = None
    outcome: str
    metadata: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = Field(None, alias="riskLevel")
    user_id: Optional[str] = Field(None, alias="userId")


class AuditEvent(BaseModel):
    """Audit event response"""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    agent_id: str = Field(..., alias="agentId")
    event_type: str = Field(..., alias="eventType")
    action: str
    resource: Optional[str] = None
    outcome: str
    timestamp: datetime
    timestamp_proof: Optional[str] = Field(None, alias="timestampProof")
    signature: Optional[str] = None
    blockchain_anchor: Optional[str] = Field(None, alias="blockchainAnchor")
    metadata: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = Field(None, alias="riskLevel")
    user_id: Optional[str] = Field(None, alias="userId")
    ledger_block_id: Optional[int] = Field(None, alias="ledgerBlockId")


class AuditEventList(BaseModel):
    """Paginated audit events"""

    events: List[AuditEvent]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")


# ============================================================================
# Policy Models
# ============================================================================


class PolicyRule(BaseModel):
    """Policy rule"""

    condition: str
    action: str
    notify: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PolicyCreate(BaseModel):
    """Policy creation request"""

    name: str
    description: Optional[str] = None
    jurisdiction: str
    rules: List[PolicyRule]
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


class Policy(BaseModel):
    """Policy response"""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    jurisdiction: str
    rules: List[PolicyRule]
    enabled: bool
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Delegation Models
# ============================================================================


class DelegationChainCreate(BaseModel):
    """Logical create request (SDK); serialized to Visual Builder POST body in delegation API."""

    model_config = ConfigDict(populate_by_name=True)

    operator_id: str = Field(..., alias="operatorId")
    primary_agent_id: str = Field(..., alias="primaryAgentId")
    delegated_agents: List[str] = Field(..., alias="delegatedAgents")
    policies: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class DelegationChain(BaseModel):
    """Delegation chain item from GET /api/v1/delegation-chains or synthesized after POST create."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chain_id: str = Field(..., alias="chainId")
    name: Optional[str] = None
    operator_id: Optional[str] = Field(None, alias="operatorId")
    primary_agent_id: Optional[str] = Field(None, alias="primaryAgentId")
    delegated_agents: List[str] = Field(default_factory=list, alias="delegatedAgents")
    status: str = "active"
    depth: Optional[int] = None
    max_depth: Optional[int] = Field(None, alias="maxDepth")
    nodes: Optional[List[Any]] = None
    source: Optional[str] = None
    policies: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    metadata: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# ============================================================================
# Verification Models
# ============================================================================


class VerificationResult(BaseModel):
    """Evidence verification result"""

    signature_valid: bool = Field(..., alias="signatureValid")
    timestamp_valid: bool = Field(..., alias="timestampValid")
    custody_intact: bool = Field(..., alias="custodyIntact")
    blockchain_verified: bool = Field(..., alias="blockchainVerified")
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Compliance Models
# ============================================================================


class ComplianceReportRequest(BaseModel):
    """POST /api/v1/audit/compliance-report body (matches backend ComplianceReportRequest)."""

    model_config = ConfigDict(populate_by_name=True)

    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    agent_ids: Optional[List[str]] = Field(None, alias="agentIds")
    report_type: str = Field("PDF", alias="reportType")


class ComplianceReportPeriod(BaseModel):
    """Period embedded in ComplianceReportResponse."""

    model_config = ConfigDict(populate_by_name=True)

    start: Optional[str] = None
    end: Optional[str] = None


class ComplianceReportSummary(BaseModel):
    """Summary embedded in ComplianceReportResponse."""

    model_config = ConfigDict(populate_by_name=True)

    total_events: int = Field(..., alias="totalEvents")
    successful_actions: int = Field(..., alias="successfulActions")
    failed_actions: int = Field(..., alias="failedActions")
    high_risk_events: int = Field(..., alias="highRiskEvents")
    compliance_score: float = Field(..., alias="complianceScore")


class ComplianceReport(BaseModel):
    """Response from POST /api/v1/audit/compliance-report."""

    model_config = ConfigDict(populate_by_name=True)

    report_id: str = Field(..., alias="reportId")
    report_type: str = Field(..., alias="reportType")
    generated_at: str = Field(..., alias="generatedAt")
    period: ComplianceReportPeriod
    summary: ComplianceReportSummary
    violations: List[Dict[str, Any]] = Field(default_factory=list)


# ============================================================================
# Tenant Models
# ============================================================================


class Tenant(BaseModel):
    """Tenant/Organization"""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    organization: Optional[str] = None
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# Statistics Models
# ============================================================================


class AgentStatistics(BaseModel):
    """Agent activity statistics"""

    model_config = ConfigDict(populate_by_name=True)

    agent_id: str = Field(..., alias="agentId")
    total_events: int = Field(..., alias="totalEvents")
    success_rate: float = Field(..., alias="successRate")
    avg_response_time: Optional[float] = Field(None, alias="avgResponseTime")
    last_activity: Optional[datetime] = Field(None, alias="lastActivity")
    risk_distribution: Optional[Dict[str, int]] = Field(None, alias="riskDistribution")
