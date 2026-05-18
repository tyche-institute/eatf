"""
Async Client Example
Demonstrates async/await usage with AsyncAletheiaClient
"""

import asyncio
from datetime import datetime
from aletheia import AsyncAletheiaClient


async def main():
    """Main async function"""
    
    # Use async context manager
    async with AsyncAletheiaClient(
        base_url="http://localhost:8081",
        email="admin@default.local",
        password="Admin123!",
        organization="default",
        auto_login=True,
    ) as client:
        
        print("✅ Authenticated successfully")
        
        # Register multiple agents concurrently
        print("\n📝 Registering multiple agents...")
        
        agents = await asyncio.gather(
            client.agents.create(
                name="GPT-4 Analyst",
                agent_type="ANALYTICAL",
                risk_classification="medium"
            ),
            client.agents.create(
                name="Claude Legal Advisor",
                agent_type="CONVERSATIONAL",
                risk_classification="high"
            ),
            client.agents.create(
                name="Gemini Researcher",
                agent_type="ANALYTICAL",
                risk_classification="low"
            )
        )
        
        print(f"✅ Registered {len(agents)} agents")
        for agent in agents:
            print(f"   - {agent.name}: {agent.agent_id}")
        
        # Log events for all agents concurrently
        print("\n📊 Logging events concurrently...")
        
        events = await asyncio.gather(
            *[
                client.audit.log_event(
                    agent_id=agent.agent_id,
                    event_type="COMPLIANCE_CHECK_PASSED",
                    action=f"analysis_{i}",
                    outcome="SUCCESS",
                    metadata={"index": i},
                    risk_level=agent.risk_classification.upper()
                )
                for i, agent in enumerate(agents)
            ]
        )
        
        print(f"✅ Logged {len(events)} events")
        for event in events:
            print(f"   - Event {event.id}: {event.action}")
        
        # Fetch audit events for all agents concurrently
        print("\n📋 Fetching audit logs...")
        
        audit_logs = await asyncio.gather(
            *[
                client.audit.list_events(agent_id=agent.agent_id, limit=10)
                for agent in agents
            ]
        )
        
        total_events = sum(len(logs) for logs in audit_logs)
        print(f"✅ Fetched {total_events} total events across all agents")
        
        # Download evidence packages concurrently
        print("\n💾 Downloading evidence packages...")
        
        evidence_packages = await asyncio.gather(
            *[
                client.audit.download_evidence(event.id)
                for event in events
            ]
        )
        
        print(f"✅ Downloaded {len(evidence_packages)} evidence packages")
        for i, evidence in enumerate(evidence_packages):
            filename = f"evidence-async-{events[i].id}.aep"
            with open(filename, "wb") as f:
                f.write(evidence)
            print(f"   - {filename} ({len(evidence)} bytes)")
        
        print("\n✅ Async example completed!")


if __name__ == "__main__":
    asyncio.run(main())
