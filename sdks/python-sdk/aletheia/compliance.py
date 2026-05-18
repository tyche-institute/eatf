"""
Compliance API — aligned with backend ComplianceController and AuditController.
"""

import json
import re
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .exceptions import AletheiaAPIError
from .models import ComplianceReport, ComplianceReportRequest

if TYPE_CHECKING:
    from .client import AletheiaClient, AsyncAletheiaClient

_END_OFFSET_TZ = re.compile(r"[+-]\d{2}:\d{2}$")


def _normalize_iso_instant(value: Optional[str]) -> Optional[str]:
    """Coerce date/datetime strings to an ISO-8601 instant Java Instant.parse accepts."""
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if v.endswith("Z"):
        return v
    if v.endswith("+00:00"):
        return v[:-6] + "Z"
    if _END_OFFSET_TZ.search(v):
        return v
    # Calendar date only
    if len(v) == 10 and v[4] == "-" and v[7] == "-":
        return f"{v}T00:00:00Z"
    # Local date-time without offset (assume UTC)
    if "T" in v:
        return v + "Z"
    return v


def _roi_from_report_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    """Derive demo ROI metrics (no dedicated /compliance/roi endpoint)."""
    tev = int(summary.get("totalEvents", 0))
    hours_per_event = 2.0
    manual_rate = 120.0
    automated_per_event = 8.0
    time_saved_hours = round(tev * hours_per_event, 2)
    manual_cost = time_saved_hours * manual_rate
    automated_cost = tev * automated_per_event
    savings = max(0.0, manual_cost - automated_cost)
    roi_pct = (savings / automated_cost * 100.0) if automated_cost > 0 else 0.0
    return {
        "manual_cost": round(manual_cost, 2),
        "automated_cost": round(automated_cost, 2),
        "savings": round(savings, 2),
        "roi_percentage": round(roi_pct, 1),
        "time_saved_hours": time_saved_hours,
        "total_events": tev,
        "compliance_score": summary.get("complianceScore"),
    }


class ComplianceAPI:
    """Synchronous Compliance API"""

    def __init__(self, client: "AletheiaClient"):
        self._client = client

    def generate_report(
        self,
        jurisdiction: str,
        start_date: str,
        end_date: str,
        format: str = "PDF",
        include_agents: Optional[List[str]] = None,
        **kwargs,
    ) -> bytes:
        """
        Generate a compliance report via POST /api/v1/audit/compliance-report.

        ``jurisdiction`` is accepted for backward compatibility and ignored (not in backend DTO).

        For ``format="JSON"``, returns the JSON response body as UTF-8 bytes.
        For ``PDF`` / other formats, downloads via GET .../compliance-report/{reportId}/download
        (MVP backend may return text/plain content).
        """
        _ = jurisdiction
        _ = kwargs.get("metadata")

        request = ComplianceReportRequest(
            start_date=_normalize_iso_instant(start_date),
            end_date=_normalize_iso_instant(end_date),
            agent_ids=include_agents,
            report_type=format,
        )
        response = self._client.request(
            "POST",
            "/api/v1/audit/compliance-report",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        report_id = response.get("reportId")
        fmt = (format or "PDF").upper()
        if fmt == "JSON":
            return json.dumps(response, indent=2, ensure_ascii=False).encode("utf-8")
        if not report_id:
            raise AletheiaAPIError("compliance-report response missing reportId")
        return self._client.download(
            f"/api/v1/audit/compliance-report/{report_id}/download?format={fmt.lower()}"
        )

    def get_report(self, report_id: str) -> ComplianceReport:
        """
        Report metadata by ID is not exposed by the API (only POST + download).
        """
        raise NotImplementedError(
            "GET report metadata by ID is not available. "
            "Use generate_report() or POST /api/v1/audit/compliance-report."
        )

    def list_reports(
        self,
        jurisdiction: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ComplianceReport]:
        """
        The backend does not provide a report catalog; returns an empty list.
        """
        _ = jurisdiction, limit, offset
        return []

    def download_report(self, report_id: str) -> bytes:
        """Download report file (MVP: text/plain body from audit download endpoint)."""
        return self._client.download(f"/api/v1/audit/compliance-report/{report_id}/download")

    def get_compliance_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Tenant summary from GET /api/v1/agents/stats, or per-agent EU AI Act check:
        GET /api/v1/compliance/eu-ai-act/{agentId}.
        """
        if agent_id:
            return self._client.request("GET", f"/api/v1/compliance/eu-ai-act/{agent_id}")
        stats = self._client.request("GET", "/api/v1/agents/stats")
        total = int(stats.get("activeAgents", 0))
        high = int(stats.get("highRiskAgents", 0))
        qual = int(stats.get("qualifiedAgents", 0))
        issues = max(0, total - qual)
        return {
            "total_agents": total,
            "high_risk_agents": high,
            "compliant": qual,
            "issues": issues,
        }

    def get_roi_calculation(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        No /compliance/roi endpoint — builds estimates from audit compliance-report summary.
        """
        request = ComplianceReportRequest(
            start_date=_normalize_iso_instant(start_date),
            end_date=_normalize_iso_instant(end_date),
            report_type="ROI",
        )
        response = self._client.request(
            "POST",
            "/api/v1/audit/compliance-report",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        summary = response.get("summary") or {}
        return _roi_from_report_summary(summary)

    def check_eu_ai_act(self, agent_id: str) -> Dict[str, Any]:
        """GET /api/v1/compliance/eu-ai-act/{agentId}"""
        return self._client.request("GET", f"/api/v1/compliance/eu-ai-act/{agent_id}")

    def agent_compliance_summary(
        self, agent_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """GET /api/v1/compliance/report/{agentId}"""
        params: Dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return self._client.request(
            "GET", f"/api/v1/compliance/report/{agent_id}", params=params or None
        )


class AsyncComplianceAPI:
    """Asynchronous Compliance API"""

    def __init__(self, client: "AsyncAletheiaClient"):
        self._client = client

    async def generate_report(
        self,
        jurisdiction: str,
        start_date: str,
        end_date: str,
        format: str = "PDF",
        include_agents: Optional[List[str]] = None,
        **kwargs,
    ) -> bytes:
        _ = jurisdiction
        _ = kwargs.get("metadata")
        request = ComplianceReportRequest(
            start_date=_normalize_iso_instant(start_date),
            end_date=_normalize_iso_instant(end_date),
            agent_ids=include_agents,
            report_type=format,
        )
        response = await self._client.request(
            "POST",
            "/api/v1/audit/compliance-report",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        report_id = response.get("reportId")
        fmt = (format or "PDF").upper()
        if fmt == "JSON":
            return json.dumps(response, indent=2, ensure_ascii=False).encode("utf-8")
        if not report_id:
            raise AletheiaAPIError("compliance-report response missing reportId")
        return await self._client.download(
            f"/api/v1/audit/compliance-report/{report_id}/download?format={fmt.lower()}"
        )

    async def get_report(self, report_id: str) -> ComplianceReport:
        raise NotImplementedError(
            "GET report metadata by ID is not available. "
            "Use generate_report() or POST /api/v1/audit/compliance-report."
        )

    async def list_reports(
        self,
        jurisdiction: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ComplianceReport]:
        _ = jurisdiction, limit, offset
        return []

    async def download_report(self, report_id: str) -> bytes:
        return await self._client.download(f"/api/v1/audit/compliance-report/{report_id}/download")

    async def get_compliance_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        if agent_id:
            return await self._client.request("GET", f"/api/v1/compliance/eu-ai-act/{agent_id}")
        stats = await self._client.request("GET", "/api/v1/agents/stats")
        total = int(stats.get("activeAgents", 0))
        high = int(stats.get("highRiskAgents", 0))
        qual = int(stats.get("qualifiedAgents", 0))
        issues = max(0, total - qual)
        return {
            "total_agents": total,
            "high_risk_agents": high,
            "compliant": qual,
            "issues": issues,
        }

    async def get_roi_calculation(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        request = ComplianceReportRequest(
            start_date=_normalize_iso_instant(start_date),
            end_date=_normalize_iso_instant(end_date),
            report_type="ROI",
        )
        response = await self._client.request(
            "POST",
            "/api/v1/audit/compliance-report",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        summary = response.get("summary") or {}
        return _roi_from_report_summary(summary)

    async def check_eu_ai_act(self, agent_id: str) -> Dict[str, Any]:
        return await self._client.request("GET", f"/api/v1/compliance/eu-ai-act/{agent_id}")

    async def agent_compliance_summary(
        self, agent_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, str] = {}
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        return await self._client.request(
            "GET", f"/api/v1/compliance/report/{agent_id}", params=params or None
        )
