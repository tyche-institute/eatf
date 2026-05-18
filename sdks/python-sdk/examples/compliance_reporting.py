"""
Compliance Reporting Example
Demonstrates generating EU AI Act compliance reports
"""

from aletheia import AletheiaClient
from datetime import UTC, datetime, timedelta

# Initialize client
client = AletheiaClient(
    base_url="http://localhost:8081",
    email="admin@default.local",
    password="Admin123!",
    organization="default",
    auto_login=True,
)

print("✅ Authenticated successfully")

# 1. Create high-risk agents for compliance demo
print("\n📝 Creating high-risk agents...")

agents = []
for i in range(3):
    agent = client.agents.create(
        name=f"High-Risk Agent {i+1}",
        agent_type="CONVERSATIONAL",
        risk_classification="high",
        capabilities=["decision_making", "customer_service"],
        primary_jurisdiction="EU",
    )
    agents.append(agent)
    print(f"   ✅ {agent.name}: {agent.agent_id}")

# 2. Log various compliance events
print("\n📊 Logging compliance events...")

for agent in agents:
    # Log decision
    client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="COMPLIANCE_CHECK_PASSED",
        action="loan_approval",
        outcome="SUCCESS",
        risk_level="HIGH",
        metadata={"amount": 50000, "approved": True}
    )
    
    # Log human review (must match backend AuditEventType enum)
    client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="HUMAN_REVIEW_APPROVED",
        action="manual_verification",
        outcome="SUCCESS",
        risk_level="HIGH",
        metadata={"reviewer": "compliance_officer_001"}
    )
    
    # Log policy evaluation
    client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="POLICY_EVALUATED",
        action="eu_ai_act_check",
        outcome="SUCCESS",
        risk_level="HIGH",
        metadata={"policy": "EU AI Act - High Risk"}
    )

print(f"✅ Logged events for {len(agents)} agents")

# 3. Get compliance status
print("\n🔍 Checking compliance status...")
status = client.compliance.get_compliance_status()
print("✅ Compliance status:")
print(f"   Total agents: {status.get('total_agents', 0)}")
print(f"   High-risk agents: {status.get('high_risk_agents', 0)}")
print(f"   Compliant: {status.get('compliant', 0)}")
print(f"   Issues: {status.get('issues', 0)}")

# 4. Generate PDF compliance report
print("\n📄 Generating PDF compliance report...")

end_date = datetime.now(UTC)
start_date = end_date - timedelta(days=30)

report_pdf = client.compliance.generate_report(
    jurisdiction="EU",
    start_date=start_date.isoformat().replace("+00:00", "Z"),
    end_date=end_date.isoformat().replace("+00:00", "Z"),
    format="PDF",
    include_agents=[agent.agent_id for agent in agents],
)

pdf_filename = f"compliance-report-{datetime.now(UTC).strftime('%Y%m%d')}.pdf"
with open(pdf_filename, "wb") as f:
    f.write(report_pdf)

print(f"✅ PDF report saved: {pdf_filename} ({len(report_pdf)} bytes)")

# 5. Generate JSON compliance report
print("\n📊 Generating JSON compliance report...")

report_json = client.compliance.generate_report(
    jurisdiction="EU",
    start_date=start_date.isoformat().replace("+00:00", "Z"),
    end_date=end_date.isoformat().replace("+00:00", "Z"),
    format="JSON",
)

json_filename = f"compliance-report-{datetime.now(UTC).strftime('%Y%m%d')}.json"
with open(json_filename, "wb") as f:
    f.write(report_json)

print(f"✅ JSON report saved: {json_filename}")

# 6. Calculate ROI
print("\n💰 Calculating compliance ROI...")
roi = client.compliance.get_roi_calculation(
    start_date=start_date.isoformat().replace("+00:00", "Z"),
    end_date=end_date.isoformat().replace("+00:00", "Z"),
)

print("✅ ROI Calculation:")
print(f"   Manual audit cost: €{roi.get('manual_cost', 0):,.2f}")
print(f"   Automated cost: €{roi.get('automated_cost', 0):,.2f}")
print(f"   Savings: €{roi.get('savings', 0):,.2f}")
print(f"   ROI: {roi.get('roi_percentage', 0):.1f}%")
print(f"   Time saved: {roi.get('time_saved_hours', 0)} hours")

# 7. Report catalog (API does not persist a list; files above are the artifacts)
print("\n📋 Compliance reports...")
reports = client.compliance.list_reports(jurisdiction="EU", limit=10)
if reports:
    print(f"✅ Found {len(reports)} reports")
    for report in reports[:5]:
        print(f"   - {report.generated_at}: {report.report_type}")
else:
    print("   (No server-side report index; use generate_report / saved files.)")

print("\n✅ Compliance reporting example completed!")
print("\n💡 Generated files:")
print(f"   - {pdf_filename}")
print(f"   - {json_filename}")
print("\n💡 View reports in UI:")
print("   - http://localhost:3000/reports")
print("   - http://localhost:3000/roi")
