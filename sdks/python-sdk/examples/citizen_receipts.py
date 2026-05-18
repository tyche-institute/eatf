"""
Citizen Receipts — minimal SDK example.

Demonstrates the EUDI Wallet × EATF flow: citizen delegates a scope
to an AI agent, the agent executes sub-actions, citizen signs final,
backend mints a VerifiableCredential of type AIDelegationReceipt.

Mirrors partner-integrations/citizen-receipts/python/run_receipt.py.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

from aletheia import AletheiaClient


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


client = AletheiaClient(
    base_url=os.environ.get("ALETHEIA_BASE_URL", "http://localhost:8081"),
    email=os.environ.get("ALETHEIA_EMAIL", "admin@default.local"),
    password=os.environ.get("ALETHEIA_PASSWORD", "Admin123!"),
    organization=os.environ.get("ALETHEIA_ORG", "default"),
    auto_login=True,
)
print("✅ Authenticated")

# 1. Mock Wallet "login"
citizen_did = f"did:web:demo-citizen-{uuid.uuid4().hex[:6]}.example.eu"
print(f"✅ Wallet login as {citizen_did}")

# 2. AI agent + delegation chain
agent = client.agents.create(
    name="Business Registry Assistant (Reference)",
    agent_type="CONVERSATIONAL",
    risk_classification="high",
)

chain = client.delegation.create_chain(
    operator_id=citizen_did,
    primary_agent_id=agent.agent_id,
    delegated_agents=[agent.agent_id],
    policies={
        "scope": "e-business:fill-form",
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(timespec="seconds"),
        "max_depth": 1,
        "allowed_actions": ["set_company_name", "set_share_capital", "set_emtak_code", "attach_articles_of_association"],
        "forbidden_actions": ["submit", "delete", "transfer"],
        "require_human_approval_before_submit": True,
    },
    metadata={"wallet_did": citizen_did, "delegation_purpose": "Estonian OÜ registration assistance"},
)
print(f"✅ Delegation chain {chain.chain_id}")

# 3. AI sub-actions (each signed)
SUB_ACTIONS = [
    ("set_company_name", {"value": "Demo OÜ"}),
    ("set_share_capital", {"value": 2500, "currency": "EUR"}),
    ("set_emtak_code", {"value": "62.01"}),
    ("attach_articles_of_association", {"hash": "sha256:abc123…"}),
]
event_ids = []
for action, payload in SUB_ACTIONS:
    ev = client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="RESPONSE_GENERATED",
        action=action,
        outcome="SUCCESS",
        metadata={"chain_id": chain.chain_id, "wallet_did": citizen_did, "payload": payload},
    )
    event_ids.append(ev.id)
    print(f"   ✓ {action}: {payload}  (event={ev.id})")

# 4. Citizen Wallet sign-off
wallet_sig = {
    "type": "WalletSignedAction",
    "did": citizen_did,
    "signed_at": now(),
    "proof_value": f"MOCK_{uuid.uuid4().hex[:8]}",
    "signed_payload": {"chain_id": chain.chain_id, "sub_actions": event_ids},
}
approval = client.audit.log_event(
    agent_id=agent.agent_id,
    event_type="HUMAN_REVIEW_APPROVED",
    action="citizen_wallet_signoff",
    outcome="SUCCESS",
    metadata={"chain_id": chain.chain_id, "wallet_did": citizen_did, "wallet_signature": wallet_sig},
)
print(f"✅ Citizen sign-off (event={approval.id})")

# 5. Print the VC shape (the backend would build this server-side and ML-DSA-sign).
vc = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://example.eatf.eu/contexts/aletheia-receipt-v1.jsonld",
    ],
    "id": f"urn:uuid:{uuid.uuid4()}",
    "type": ["VerifiableCredential", "AIDelegationReceipt"],
    "issuer": "did:web:eatf.example.eu",
    "issuanceDate": now(),
    "credentialSubject": {
        "id": citizen_did,
        "delegation": {"chain_id": chain.chain_id, "scope": "e-business:fill-form"},
        "actions": [{"id": eid, "action": SUB_ACTIONS[i][0]} for i, eid in enumerate(event_ids)],
        "approval_event_id": approval.id,
        "wallet_signature": wallet_sig,
    },
    "proof": {
        "type": "MlDsa65Signature2026",
        "verificationMethod": "did:web:eatf.example.eu#key-mldsa-2026",
        "proofValue": f"PROD_BACKEND_WOULD_SIGN_{chain.chain_id[:8]}",
    },
}
print("\n📜 AIDelegationReceipt VC (preview):")
print(json.dumps(vc, indent=2, ensure_ascii=False)[:800])
print(f"\n📦 Bundle URL: {client.config.base_url}/api/v1/evidence/by-chain/{chain.chain_id}?as=vc")
print("\n✅ citizen_receipts example completed")
