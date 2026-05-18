"""
OpenCourt — forensic-ledger demo for AI-assisted legal case prep.

Three-role pipeline:
  researcher  → gathers precedents (12 signed query events)
  drafter     → produces 3 iterations of a complaint draft (3 signed actions)
  reviewer    → human partner makes 7 edits and signs final (1 human-approval event)

Every step lands in the hash-chained audit ledger and ends up in a single
`.aep` evidence package that can be verified offline. On stage we cut Wi-Fi
and run `eatf verify --offline --print-chain` to prove the bundle stands
on its own — no backend round-trip needed.

Annex III(8)(a) — administration of justice. AI Act Art 12, 13, 14.
"""

import os
import time
from aletheia import AletheiaClient

BASE_URL = os.environ.get("ALETHEIA_BASE_URL", "http://localhost:8081")

client = AletheiaClient(
    base_url=BASE_URL,
    email=os.environ.get("ALETHEIA_EMAIL", "admin@default.local"),
    password=os.environ.get("ALETHEIA_PASSWORD", "Admin123!"),
    organization=os.environ.get("ALETHEIA_ORG", "default"),
    auto_login=True,
)
print("✅ Authenticated")

# 1. Three role-specific agents. Risk classification follows the actual blast
#    radius of each role: a researcher only reads, a drafter produces text the
#    partner will edit, a reviewer represents the human partner herself.
print("\n📝 Provisioning OpenCourt agents...")

orchestrator = client.agents.create(
    name="OpenCourt Orchestrator",
    agent_type="CONVERSATIONAL",
    risk_classification="high",
    description="Coordinates legal case prep across researcher/drafter/reviewer",
)
researcher = client.agents.create(
    name="OpenCourt Researcher",
    agent_type="ANALYTICAL",
    risk_classification="medium",
    description="Searches precedents and statute for GDPR Art 17 cases",
)
drafter = client.agents.create(
    name="OpenCourt Drafter",
    agent_type="CONVERSATIONAL",
    risk_classification="medium",
    description="Generates iterative complaint drafts",
)
reviewer = client.agents.create(
    name="OpenCourt Partner-Reviewer",
    agent_type="ANALYTICAL",
    risk_classification="high",
    description="Human partner stand-in for final review and edits",
)
print(f"✅ Orchestrator {orchestrator.agent_id}")
print(f"✅ Researcher   {researcher.agent_id}")
print(f"✅ Drafter      {drafter.agent_id}")
print(f"✅ Reviewer     {reviewer.agent_id}")

# 2. Delegation chain: Sorainen-OÜ → Riin (partner) → Orchestrator → {researcher, drafter, reviewer}
print("\n🔗 Creating delegation chain...")
chain = client.delegation.create_chain(
    operator_id="riin.partner@sorainen.example",
    primary_agent_id=orchestrator.agent_id,
    delegated_agents=[researcher.agent_id, drafter.agent_id, reviewer.agent_id],
    policies={
        "max_depth": 2,
        "require_approval": True,
        "allowed_actions": ["read", "search", "draft", "review", "sign"],
        "forbidden_actions": ["file", "submit-to-court", "delete"],
        "timeout_seconds": 7200,
        "human_review_threshold": "ANY_FINAL_DRAFT",
        "case_reference": "GDPR-Art17-erasure-failed-2026Q2",
    },
    metadata={
        "purpose": "Legal complaint preparation pipeline",
        "firm": "Sorainen OÜ",
        "matter": "GDPR Art 17 — right to erasure failed",
        "jurisdiction": "EE",
    },
)
print(f"✅ Chain {chain.chain_id} (status={chain.status})")

# 3. Researcher: 12 precedent queries. Each is a signed event in the ledger.
print("\n🔍 Researcher gathering 12 precedents...")
precedent_topics = [
    "CJEU Google Spain (C-131/12) — right to be forgotten scope",
    "EDPB Guidelines 5/2019 on Art 17",
    "EE Andmekaitse Inspektsioon practice 2024-2026",
    "GDPR Art 17(1)(a) — purpose limitation",
    "GDPR Art 17(3) — exemptions",
    "Recital 65 — public interest balance",
    "Recital 66 — practical erasure measures",
    "Tartu Ringkonnakohus 2-22-1234 (mock)",
    "Riigikohus 3-21-987 (mock)",
    "ECtHR Big Brother Watch — proportionality",
    "Norra DPA decision 22/01445 — backup erasure",
    "WP29 Opinion 4/2007 on personal data concept",
]
for i, topic in enumerate(precedent_topics, 1):
    ev = client.audit.log_event(
        agent_id=researcher.agent_id,
        event_type="RESPONSE_GENERATED",
        action=f"precedent_query_{i:02d}",
        outcome="SUCCESS",
        metadata={"topic": topic, "chain_id": chain.chain_id, "step": "research"},
    )
    print(f"   {i:02d}. {topic[:60]}…  ({ev.id})")

# 4. Drafter: 3 iterations. Diff between iterations is the AI Act Art 13 transparency surface.
print("\n✍️  Drafter producing 3 iterations...")
iterations = [
    ("v0.1", "First skeleton: facts, legal basis, prayer for relief.", 1240),
    ("v0.2", "Added precedent citations from research phase.", 1815),
    ("v0.3", "Tightened Art 17(3) carve-out analysis; added remedies.", 2104),
]
for ver, summary, words in iterations:
    ev = client.audit.log_event(
        agent_id=drafter.agent_id,
        event_type="RESPONSE_GENERATED",
        action=f"draft_{ver}",
        outcome="SUCCESS",
        metadata={
            "version": ver,
            "summary": summary,
            "word_count": words,
            "chain_id": chain.chain_id,
            "step": "drafting",
        },
    )
    print(f"   {ver}: {summary} ({words} words, ev={ev.id})")

# 5. Reviewer (human stand-in): 7 edits, then signed approval.
print("\n👤 Riin (partner) makes 7 edits, signs final draft...")
edits = [
    "Reword opening para — too informal",
    "Insert §14 of EE Personal Data Protection Act",
    "Drop unsupported damages claim",
    "Tighten reference to Art 17(3)(e)",
    "Add timeline: data subject notice → controller silence → complaint",
    "Adjust prayer for relief to fit DPA jurisdiction",
    "Final proof-read pass",
]
for i, edit in enumerate(edits, 1):
    ev = client.audit.log_event(
        agent_id=reviewer.agent_id,
        event_type="RESPONSE_GENERATED",
        action=f"human_edit_{i:02d}",
        outcome="SUCCESS",
        metadata={"edit": edit, "chain_id": chain.chain_id, "step": "review"},
    )
    print(f"   ✏️  {edit}")

approval = client.audit.log_event(
    agent_id=reviewer.agent_id,
    event_type="HUMAN_REVIEW_APPROVED",
    action="partner_signoff",
    outcome="SUCCESS",
    metadata={
        "approved_by": "riin.partner@sorainen.example",
        "signed_via": "mTLS clientside cert",
        "final_word_count": 2098,
        "chain_id": chain.chain_id,
        "step": "signoff",
    },
)
print(f"✅ Final partner sign-off event: {approval.id}")

# 6. Verify the chain and surface the audit count.
print("\n🔎 Verifying chain integrity...")
is_valid = client.delegation.verify_chain(chain.chain_id)
print(f"✅ Chain valid: {is_valid}")

agent_audit = client.audit.list_events(agent_id=orchestrator.agent_id, limit=100)
print(f"📋 Orchestrator-scoped audit events: {len(agent_audit)}")

# 7. Hint at offline verification — actually exercising it lives in run.sh.
print("\n📦 Bundle exportable as .aep:")
print(f"   curl -H 'Authorization: Bearer $EATF_API_KEY' \\")
print(f"        '{BASE_URL}/api/v1/evidence/by-chain/{chain.chain_id}?format=zip' -o opencourt.aep")
print(f"   eatf verify opencourt.aep --offline --print-chain")

print("\n✅ OpenCourt SDK example completed")
print(f"   View chain: {BASE_URL.replace('8081', '3000')}/scenarios/court?chain={chain.chain_id}")
