"""
Delegation Chains Example
Demonstrates multi-level agent delegation with policy enforcement
"""

from aletheia import AletheiaClient

# Initialize client
client = AletheiaClient(
    base_url="http://localhost:8081",
    email="admin@default.local",
    password="Admin123!",
    organization="default",
    auto_login=True,
)

print("✅ Authenticated successfully")

# 1. Create agents for delegation chain
print("\n📝 Creating agents for delegation chain...")

# Primary agent
primary_agent = client.agents.create(
    name="GPT-4 Orchestrator",
    agent_type="CONVERSATIONAL",
    risk_classification="high",
    description="Primary agent that coordinates tasks"
)
print(f"✅ Primary agent: {primary_agent.agent_id}")

# Delegated agents
researcher = client.agents.create(
    name="Research Assistant",
    agent_type="ANALYTICAL",
    risk_classification="medium"
)
print(f"✅ Researcher: {researcher.agent_id}")

writer = client.agents.create(
    name="Content Writer",
    agent_type="CONVERSATIONAL",
    risk_classification="low"
)
print(f"✅ Writer: {writer.agent_id}")

reviewer = client.agents.create(
    name="Quality Reviewer",
    agent_type="ANALYTICAL",
    risk_classification="medium"
)
print(f"✅ Reviewer: {reviewer.agent_id}")

# 2. Create delegation chain
print("\n🔗 Creating delegation chain...")

chain = client.delegation.create_chain(
    operator_id="operator-001",
    primary_agent_id=primary_agent.agent_id,
    delegated_agents=[
        researcher.agent_id,
        writer.agent_id,
        reviewer.agent_id
    ],
    policies={
        "max_depth": 3,
        "require_approval": True,
        "allowed_actions": ["read", "analyze", "generate", "review"],
        "forbidden_actions": ["delete", "execute"],
        "timeout_seconds": 3600,
        "human_review_threshold": "HIGH"
    },
    metadata={
        "purpose": "Content creation pipeline",
        "created_by": "admin"
    }
)

print(f"✅ Delegation chain created: {chain.chain_id}")
print(f"   Status: {chain.status}")
print(f"   Primary agent: {chain.primary_agent_id}")
print(f"   Delegated agents: {len(chain.delegated_agents)}")

# 3. Verify delegation chain
print("\n🔍 Verifying delegation chain...")
is_valid = client.delegation.verify_chain(chain.chain_id)
print(f"✅ Chain valid: {is_valid}")

# 4. Log events through delegation chain
print("\n📊 Logging events through delegation chain...")

# Primary agent delegates to researcher (must match backend AuditEventType enum)
event1 = client.audit.log_event(
    agent_id=primary_agent.agent_id,
    event_type="DELEGATION_CREATED",
    action="delegate_research",
    outcome="SUCCESS",
    metadata={
        "delegated_to": researcher.agent_id,
        "task": "Research AI regulations",
        "chain_id": chain.chain_id
    }
)
print(f"✅ Primary → Researcher: {event1.id}")

# Researcher performs task
event2 = client.audit.log_event(
    agent_id=researcher.agent_id,
    event_type="RESPONSE_GENERATED",
    action="research_completed",
    outcome="SUCCESS",
    metadata={
        "findings": "EU AI Act compliance requirements",
        "chain_id": chain.chain_id
    }
)
print(f"✅ Researcher completed: {event2.id}")

# Primary delegates to writer
event3 = client.audit.log_event(
    agent_id=primary_agent.agent_id,
    event_type="DELEGATION_CREATED",
    action="delegate_writing",
    outcome="SUCCESS",
    metadata={
        "delegated_to": writer.agent_id,
        "task": "Write article based on research",
        "chain_id": chain.chain_id
    }
)
print(f"✅ Primary → Writer: {event3.id}")

# Writer completes task
event4 = client.audit.log_event(
    agent_id=writer.agent_id,
    event_type="RESPONSE_GENERATED",
    action="content_generated",
    outcome="SUCCESS",
    metadata={
        "content_length": 1500,
        "chain_id": chain.chain_id
    }
)
print(f"✅ Writer completed: {event4.id}")

# Primary delegates to reviewer
event5 = client.audit.log_event(
    agent_id=primary_agent.agent_id,
    event_type="DELEGATION_CREATED",
    action="delegate_review",
    outcome="SUCCESS",
    metadata={
        "delegated_to": reviewer.agent_id,
        "task": "Review and approve content",
        "chain_id": chain.chain_id
    }
)
print(f"✅ Primary → Reviewer: {event5.id}")

# Reviewer completes
event6 = client.audit.log_event(
    agent_id=reviewer.agent_id,
    event_type="HUMAN_REVIEW_APPROVED",
    action="review_approved",
    outcome="SUCCESS",
    metadata={
        "quality_score": 0.95,
        "approved": True,
        "chain_id": chain.chain_id
    }
)
print(f"✅ Reviewer completed: {event6.id}")

# 5. List all delegations for primary agent
print("\n📋 Listing delegations for primary agent...")
delegations = client.delegation.get_agent_delegations(primary_agent.agent_id)
print(f"✅ Found {len(delegations)} delegation chains")

# 6. Get delegation chain details
print("\n🔍 Getting chain details...")
chain_details = client.delegation.get_chain(chain.chain_id)
print(f"✅ Chain: {chain_details.chain_id}")
print(f"   Status: {chain_details.status}")
print(f"   Created: {chain_details.created_at}")
print(f"   Policies: {chain_details.policies}")

print("\n✅ Delegation chain example completed!")
print("\n💡 Next steps:")
print(f"   - View chain: http://localhost:3000/delegation-chains")
print(f"   - View 3D graph: http://localhost:3000/delegation-chains/3d")
print(f"   - Verify events in audit log: http://localhost:3000/audit")
