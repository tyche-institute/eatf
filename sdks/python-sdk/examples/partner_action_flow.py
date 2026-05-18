#!/usr/bin/env python3
"""
Partner demo: login → register agent → action request → approve.

Preferred auth — use a long-lived API key minted at /settings → API keys:

  export ALETHEIA_BASE_URL=http://localhost:8081
  export ALETHEIA_API_KEY=alth_live_...
  python examples/partner_action_flow.py

Fallback for interactive testing — email + password (short-lived JWT):

  export ALETHEIA_BASE_URL=http://localhost:8081
  export ALETHEIA_EMAIL=admin@default.local
  export ALETHEIA_PASSWORD='Admin123!'
  python examples/partner_action_flow.py
"""

import os
import sys
import time

from aletheia import AletheiaClient


def main() -> int:
    base = os.environ.get("ALETHEIA_BASE_URL", "http://localhost:8081").rstrip("/")
    api_key = os.environ.get("ALETHEIA_API_KEY")
    if api_key:
        client = AletheiaClient(base_url=base, token=api_key)
    else:
        email = os.environ.get("ALETHEIA_EMAIL", "admin@default.local")
        password = os.environ.get("ALETHEIA_PASSWORD", "Admin123!")
        client = AletheiaClient(
            base_url=base, email=email, password=password, auto_login=True
        )

    stamp = int(time.time())
    agent = client.agents.create(
        name=f"partner-demo-{stamp}",
        agent_type="CONVERSATIONAL",
        risk_classification="limited",
        capabilities=["demo"],
        primary_jurisdiction="EU",
    )
    print("Agent:", agent.agent_id)

    req = client.actions.create_request(
        agent_id=agent.agent_id,
        action_type="PAYMENT_INTENT",
        payload={"amount": 42, "currency": "EUR", "note": "partner_action_flow.py"},
        correlation_id=f"py-demo-{stamp}",
        requested_by="partner_action_flow.py",
    )
    print("Request:", req.request_id, "status=", req.status, "audit=", req.create_audit_event_id)

    approved = client.actions.approve(
        req.request_id, comment="demo approve", decided_by="python-demo"
    )
    print("Final:", approved.status, "decision_audit=", approved.decision_audit_event_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
