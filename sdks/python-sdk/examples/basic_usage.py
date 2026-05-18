"""
Basic Usage Example
Demonstrates agent registration, event logging, and evidence download
"""

from aletheia import AletheiaClient
from datetime import UTC, datetime

# Initialize client
client = AletheiaClient(
    base_url="http://localhost:8081",
    email="admin@default.local",
    password="Admin123!",
    organization="default",
    auto_login=True,
)

print("✅ Authenticated successfully")

# 1. Register a new AI agent
print("\n📝 Registering agent...")
agent = client.agents.create(
    name="GPT-4 Customer Service",
    agent_type="CONVERSATIONAL",
    risk_classification="limited",
    capabilities=["text_generation", "qa", "summarization"],
    primary_jurisdiction="EU",
    description="AI agent for customer support"
)

print(f"✅ Agent registered: {agent.agent_id}")
print(f"   Name: {agent.name}")
print(f"   Type: {agent.agent_type}")
print(f"   Risk: {agent.risk_classification}")

# 2. Log a decision
print("\n📊 Logging AI decision...")
event = client.audit.log_event(
    agent_id=agent.agent_id,
    event_type="COMPLIANCE_CHECK_PASSED",
    action="customer_refund_approval",
    resource="ticket/12345",
    outcome="SUCCESS",
    metadata={
        "customer_id": "CUST-9876",
        "refund_amount": 149.99,
        "reason": "Product defect",
        "timestamp": datetime.now(UTC).isoformat()
    },
    risk_level="HIGH"
)

print(f"✅ Event logged: {event.id}")
print(f"   Timestamp: {event.timestamp}")
print(f"   Signature: {event.signature[:50] if event.signature else 'N/A'}...")
print(f"   Timestamp proof: {event.timestamp_proof[:50] if event.timestamp_proof else 'N/A'}...")

# 3. Fetch raw audit event JSON (for .aep use GET /api/ai/evidence/{responseId})
print("\n💾 Downloading audit event JSON...")
evidence = client.audit.download_evidence(event.id)

filename = f"audit-event-{event.id}.json"
with open(filename, "wb") as f:
    f.write(evidence)

print(f"✅ Saved: {filename} ({len(evidence)} bytes)")

# 4. List audit events
print("\n📋 Listing recent events...")
events = client.audit.list_events(
    agent_id=agent.agent_id,
    limit=10
)

print(f"✅ Found {len(events)} events")
for evt in events[:3]:
    print(f"   - {evt.timestamp}: {evt.action} → {evt.outcome}")

# 5. Get agent details
print("\n🔍 Fetching agent details...")
agent_details = client.agents.get(agent.agent_id)
print(f"✅ Agent: {agent_details.name}")
print(f"   Status: {agent_details.status}")
print(f"   Registered: {agent_details.registered_at}")

# 6. List all agents
print("\n📋 Listing all agents...")
all_agents = client.agents.list()
print(f"✅ Total agents: {len(all_agents)}")
for ag in all_agents[:5]:
    print(f"   - {ag.name} ({ag.agent_type})")

print("\n✅ Example completed successfully!")
print("\n💡 Next steps:")
print("   - Check the evidence file:", filename)
print("   - View agent in UI: http://localhost:3000/agents/" + agent.agent_id)
print("   - View audit log: http://localhost:3000/audit")
