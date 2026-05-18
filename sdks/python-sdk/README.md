# Aletheia AI Python SDK

Python client library for the Aletheia AI Agent Trust Framework - enterprise-grade AI governance, EU AI Act compliance, and cryptographic audit trails.

[![PyPI version](https://badge.fury.io/py/aletheia-ai.svg)](https://badge.fury.io/py/aletheia-ai)
[![Python Support](https://img.shields.io/pypi/pyversions/aletheia-ai.svg)](https://pypi.org/project/aletheia-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔐 **Cryptographic Audit Trails** - RSA + ML-DSA (post-quantum) signatures
- 🏛️ **EU AI Act Compliant** - Built-in compliance reporting
- 🤖 **Agent Lifecycle Management** - Registration, monitoring, delegation chains
- 📊 **Real-time Monitoring** - WebSocket support for live agent activity
- 🔗 **Delegation Chains** - Multi-level agent delegation with policy enforcement
- 📝 **Evidence Packages** - Legally-admissible audit evidence (AEP format)
- 🌍 **Multi-tenant** - Organization and tenant isolation

## Installation

```bash
pip install aletheia-ai
```

## Quick Start

### 1. Authentication

Uses **`POST /api/auth/credentials`** (returns `accessToken`). Optional `organization=` maps to `tenantKey` in the JSON body.

```python
from aletheia import AletheiaClient

# Initialize client (no network I/O at construction time)
client = AletheiaClient(
    base_url="https://api.aletheia.ai",
    email="your-email@example.com",
    password="your-password",
)
client.login(client.config.email, client.config.password)

# Or let the constructor authenticate for you
client = AletheiaClient(
    base_url="https://api.aletheia.ai",
    email="your-email@example.com",
    password="your-password",
    auto_login=True,
)

# Or use an existing token
client = AletheiaClient(
    base_url="https://api.aletheia.ai",
    token="your-jwt-token",
)
```

### 2. Register an AI Agent

```python
# Register a new agent (POST /api/v1/agents/register)
agent = client.agents.create(
    name="GPT-4 Assistant",
    agent_type="CONVERSATIONAL",
    risk_classification="limited",
    capabilities=["text_generation", "qa"],
    primary_jurisdiction="EU",
)

print(f"Agent registered: {agent.agent_id}")
```

### 3. Log AI Decisions

```python
from datetime import UTC, datetime

# Log a high-risk decision (event_type must match backend AuditEventType enum)
event = client.audit.log_event(
    agent_id=agent.agent_id,
    event_type="COMPLIANCE_CHECK_PASSED",
    action="loan_approval",
    resource="application/loan-12345",
    outcome="SUCCESS",
    metadata={
        "loan_amount": 50000,
        "credit_score": 720,
        "decision": "approved",
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    },
    risk_level="HIGH",
)

print(f"Decision logged: {event.id}")
print(f"Timestamp proof: {event.timestamp_proof}")

# Audit event JSON (for AI Evidence Packages use GET /api/ai/evidence/{id} on the backend)
evidence = client.audit.download_evidence(event.id)
with open("audit-event.json", "wb") as f:
    f.write(evidence)
```

### 4. Query Audit Logs

```python
# Search audit events
events = client.audit.list_events(
    agent_id=agent.agent_id,
    event_type="COMPLIANCE_CHECK_PASSED",
    start_date="2026-01-01",
    limit=100
)

for event in events:
    print(f"{event.timestamp} - {event.action}: {event.outcome}")
```

### 5. Delegation Chains

Uses **`POST /api/v1/delegation-chains`** (hyphenated). The SDK maps your arguments to the Visual Builder `nodes` JSON; `verify_chain` checks the chain appears in **`GET /api/v1/delegation-chains`**. There is no server route to revoke a chain via the SDK.

```python
# Create delegation chain
chain = client.delegation.create_chain(
    operator_id="operator-123",
    primary_agent_id=agent.agent_id,
    delegated_agents=["agent-456", "agent-789"],
    policies={
        "max_depth": 3,
        "require_approval": True,
        "allowed_actions": ["read", "analyze"]
    }
)

# Verify delegation is valid
is_valid = client.delegation.verify_chain(chain.chain_id)
print(f"Delegation chain valid: {is_valid}")
```

## API alignment with this backend

The client in this repo tracks the **Spring Boot** controllers:

| Area | Notes |
|------|--------|
| **Audit** | `event_type` must be a name from `AuditEventType` in the backend (e.g. `DELEGATION_CREATED`, `RESPONSE_GENERATED`, not fictional types like `TASK_COMPLETED`). |
| **Delegation** | Base path **`/api/v1/delegation-chains`**. No `GET .../{chainId}`; `get_chain` scans the list. `revoke_chain` is not supported by the API. |
| **Compliance** | `generate_report` → `POST /api/v1/audit/compliance-report` (+ file download for non-JSON). `get_compliance_status()` without `agent_id` → `GET /api/v1/agents/stats`. `get_roi_calculation()` uses the report summary (no `/compliance/roi`). `list_reports()` returns `[]` (no report catalog API). |
| **Attestations** | `client.attestations.list_policies()` → `GET /api/v1/policy-registry` (valid `policy_id` values). `client.attestations.attest(agent_id, action_type, input, output, policy_id, policy_version)` → `POST /api/v1/attest`. `agent_id` must be the full `urn:uuid:<uuid>` form returned by registration. |

See `docs/api/REST-API.md` for the full route index. Partner onboarding checklist and
gotchas live in `partner-integrations/README.md`.

## Async Support

All methods support async/await:

```python
import asyncio
from aletheia import AsyncAletheiaClient

async def main():
    async with AsyncAletheiaClient(
        base_url="https://api.aletheia.ai",
        email="your-email@example.com",
        password="your-password",
        auto_login=True,
    ) as client:
        # Register agent
        agent = await client.agents.create(
            name="Async Agent",
            agent_type="CONVERSATIONAL"
        )
        
        # Log decision
        event = await client.audit.log_event(
            agent_id=agent.agent_id,
            event_type="COMPLIANCE_CHECK_PASSED",
            action="prediction",
            outcome="SUCCESS"
        )
        
        print(f"Event logged: {event.id}")

asyncio.run(main())
```

## Real-time Monitoring

```python
# Subscribe to agent events via WebSocket
def on_event(event):
    print(f"Live event: {event.event_type} - {event.action}")

client.monitoring.subscribe(
    agent_id=agent.agent_id,
    callback=on_event
)

# Keep connection alive
client.monitoring.run()
```

## Advanced Features

### Policy Management

```python
# Create compliance policy
policy = client.policies.create(
    name="EU AI Act - High Risk",
    jurisdiction="EU",
    rules=[
        {
            "condition": "risk_level == 'HIGH'",
            "action": "require_human_review",
            "notify": ["compliance@company.com"]
        }
    ]
)

# Apply policy to agent
client.agents.attach_policy(agent.agent_id, policy.id)
```

### Verification

```python
# Verify cryptographic evidence
verification = client.verification.verify_evidence(
    evidence_file="evidence.aep"
)

print(f"Signature valid: {verification.signature_valid}")
print(f"Timestamp valid: {verification.timestamp_valid}")
print(f"Chain of custody intact: {verification.custody_intact}")
```

### Compliance Reports

```python
# Generate compliance report (POST /api/v1/audit/compliance-report; use ISO-8601 instants for dates)
report = client.compliance.generate_report(
    jurisdiction="EU",  # accepted for API compatibility; not sent to backend DTO
    start_date="2026-01-01T00:00:00Z",
    end_date="2026-12-31T23:59:59Z",
    format="PDF",
)

# Download report (MVP download may be text/plain; filename in Content-Disposition may still be .txt)
with open("compliance-report-2026.pdf", "wb") as f:
    f.write(report)
```

## Error Handling

```python
from aletheia.exceptions import (
    AletheiaAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError
)

try:
    agent = client.agents.get("invalid-id")
except NotFoundError:
    print("Agent not found")
except AuthenticationError:
    print("Invalid credentials")
except ValidationError as e:
    print(f"Validation error: {e.details}")
except AletheiaAPIError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

## Configuration

```python
from aletheia import AletheiaClient, Config

config = Config(
    base_url="https://api.aletheia.ai",
    timeout=30.0,
    max_retries=3,
    verify_ssl=True,
    log_level="INFO"
)

client = AletheiaClient.from_config(config)
```

## Examples

See the [`examples/`](./examples/) directory for complete examples:

- [`basic_usage.py`](./examples/basic_usage.py) - Basic agent registration and logging
- [`async_client.py`](./examples/async_client.py) - Async/await usage
- [`delegation_chains.py`](./examples/delegation_chains.py) - Multi-level delegation
- [`real_time_monitoring.py`](./examples/real_time_monitoring.py) - WebSocket monitoring
- [`compliance_reporting.py`](./examples/compliance_reporting.py) - Generate compliance reports

## Documentation

Full documentation available at: https://docs.aletheia.ai/sdk/python

- [API Reference](https://docs.aletheia.ai/sdk/python/api)
- [User Guide](https://docs.aletheia.ai/sdk/python/guide)
- [Advanced Topics](https://docs.aletheia.ai/sdk/python/advanced)

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.0.0

## Development

```bash
# Clone repository
git clone https://github.com/aletheia-ai/python-sdk.git
cd python-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy aletheia/

# Format code
black aletheia/ tests/
ruff check aletheia/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@aletheia.ai
- 💬 Discord: https://discord.gg/aletheia-ai
- 📚 Documentation: https://docs.aletheia.ai
- 🐛 Issues: https://github.com/aletheia-ai/python-sdk/issues

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

**Built with ❤️ for trustworthy AI governance**
