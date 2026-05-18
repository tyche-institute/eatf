"""
Bürokratt Accountability Kit — minimal SDK example.

Shows how a Bürokratt-style agent in the Estonian Bürokratt 2026 network
opts into the Aletheia Accountability Kit:

    1. Register the agent with v0.1 Kratt manifest fields (kratt_id, risk_class).
    2. Sign each citizen Q&A round-trip.
    3. Queue a human-review event when the prompt hits a HIGH-risk policy.
    4. Surface the evidence URL.

Spec: docs/specs/kratt-manifest.md.
This example does NOT pretend to belong to any Estonian institution.
"""

from __future__ import annotations
import os
from aletheia import AletheiaClient

client = AletheiaClient(
    base_url=os.environ.get("ALETHEIA_BASE_URL", "http://localhost:8081"),
    email=os.environ.get("ALETHEIA_EMAIL", "admin@default.local"),
    password=os.environ.get("ALETHEIA_PASSWORD", "Admin123!"),
    organization=os.environ.get("ALETHEIA_ORG", "default"),
    auto_login=True,
)
print("✅ Authenticated")

# 1. Provision (or re-fetch) the reference Kratt agent.
agent = client.agents.create(
    name="Aletheia Reference Kratt",
    agent_type="CONVERSATIONAL",
    risk_classification="high",
    description="Reference Bürokratt-style agent demonstrating Aletheia governance",
)
print(f"✅ Kratt agent registered: {agent.agent_id}")

KRATT_ID = "aletheia-reference"

# 2. Three illustrative citizen prompts in Estonian. The middle one is HIGH
#    risk and triggers a human-review queue event.
rounds = [
    ("Mis dokumendid on vaja OÜ asutamiseks?", "LOW",
     "OÜ asutamiseks on vaja: ID-kaarti, ettevõtte nime, EMTAK koodi, põhikirja ja osakapitali."),
    ("Kas mul on õigus töötutoetusele?", "HIGH",
     "Töötutoetuse õiguse hindab Töötukassa konkreetse tööalase ajaloo põhjal — palun pöörduge nende poole."),
    ("Kuidas registreerida elukohta uues linnas?", "LOW",
     "Logige sisse rahvastikuregistri portaali või minge kohaliku omavalitsuse teenindusbüroosse."),
]

for prompt, risk, answer in rounds:
    print(f"\n📩 {prompt}")
    print(f"💬 {answer}")

    # 3. Log every Q&A as a signed audit event (uses audit.log_event; for raw
    #    PKI signing call POST /api/sign directly — see eu-ai-act-agent example).
    stamp = client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="RESPONSE_GENERATED",
        action="sign_qa_round",
        outcome="SUCCESS",
        metadata={
            "kratt_id": KRATT_ID,
            "risk_class": risk,
            "language": "et",
            "citizen_pseudonym": "demo-citizen-001",
            "prompt": prompt,
            "response": answer,
        },
    )
    print(f"   🖋  event_id={stamp.id}")

    # 4. HIGH risk — queue a human-review event in the audit ledger.
    if risk == "HIGH":
        ev = client.audit.log_event(
            agent_id=agent.agent_id,
            event_type="HUMAN_REVIEW_REQUESTED",
            action="benefit_eligibility_query",
            outcome="QUEUED",
            metadata={
                "kratt_id": KRATT_ID,
                "stamp_event_id": stamp.id,
                "policy_hit": "benefits_eligibility",
            },
        )
        print(f"   ⏸  human review queued (event={ev.id})")

print(f"\n📦 Reach evidence at:")
print(f"   {client.config.base_url}/api/v1/evidence/by-kratt/{KRATT_ID}")
print(f"\n🔖 Embed badge anywhere:")
print(f"   <script src=\"https://example.eatf.eu/badge.js\" data-kratt=\"{KRATT_ID}\" async></script>")
print("\n✅ burokratt_kit example completed")
