"""
School Compass — minimal SDK example.

Shows the Annex III(3) education flow: AI proposes a grade with a
rationale, the teacher accepts or overrides, every decision is signed
and ends up in a per-student evidence package.

This file mirrors partner-integrations/school-compass/python/grade_batch.py
but compresses to a single small script suitable for the examples/ folder.
"""

from __future__ import annotations

import hashlib
import json
import os
import random

from aletheia import AletheiaClient


client = AletheiaClient(
    base_url=os.environ.get("ALETHEIA_BASE_URL", "http://localhost:8081"),
    email=os.environ.get("ALETHEIA_EMAIL", "admin@default.local"),
    password=os.environ.get("ALETHEIA_PASSWORD", "Admin123!"),
    organization=os.environ.get("ALETHEIA_ORG", "default"),
    auto_login=True,
)
print("✅ Authenticated")

agent = client.agents.create(
    name="School Compass — Reference Grader",
    agent_type="ANALYTICAL",
    risk_classification="high",
    description="Reference Kratt for AI-assisted essay grading with mandatory teacher sign-off",
)
print(f"✅ Grader agent {agent.agent_id}")

KRATT_ID = "school-compass-reference"

ESSAYS = [
    {"student_id": "stud-901", "title": "Mu lemmik aastaaeg",
     "text": "Mu lemmik aastaaeg on sügis. Sügisel on lehed kollased ja punased. Mulle meeldib jalutada metsas."},
    {"student_id": "stud-902", "title": "Tehnoloogia minu elus",
     "text": "Tehnoloogia muudab meie elu. Pean oluliseks leida tasakaal — kasutada tehnoloogiat targalt."},
    {"student_id": "stud-903", "title": "Sõpruse tähendus",
     "text": "Sõprus on minu jaoks usaldus. Hea sõber on see, kes on olemas raskel hetkel."},
]


def hash_essay(e):
    return hashlib.sha256(json.dumps(
        {"student_id": e["student_id"], "title": e["title"], "text": e["text"]},
        sort_keys=True,
    ).encode("utf-8")).hexdigest()


def heuristic_grade(text: str) -> tuple[int, str]:
    wc = len(text.split())
    grade = 5 if wc > 33 else 4 if wc > 18 else 3
    return grade, f"Word count {wc}; arguments {'clear' if grade == 5 else 'traceable' if grade == 4 else 'limited'}."


for essay in ESSAYS:
    grade, rationale = heuristic_grade(essay["text"])
    essay_hash = hash_essay(essay)

    sugg = client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="RESPONSE_GENERATED",
        action="ai_grade_suggestion",
        outcome="SUCCESS",
        metadata={
            "kratt_id": KRATT_ID,
            "essay_hash": essay_hash,
            "student_id": essay["student_id"],
            "stage": "ai_suggestion",
            "suggested_grade": grade,
            "rationale": rationale,
        },
    )

    is_override = random.random() < 0.2
    final_grade = grade if not is_override else max(3, grade - 1)
    decision = client.audit.log_event(
        agent_id=agent.agent_id,
        event_type="HUMAN_REVIEW_APPROVED",
        action="teacher_grade_decision",
        outcome="SUCCESS",
        metadata={
            "suggestion_event_id": sugg.id,
            "student_id": essay["student_id"],
            "essay_hash": essay_hash,
            "ai_suggested_grade": grade,
            "final_grade": final_grade,
            "override": is_override,
            "kratt_id": KRATT_ID,
            "stage": "teacher_decision",
        },
    )
    print(f"   {essay['student_id']}: AI={grade} → final={final_grade} ({'override' if is_override else 'accept'}, decision={decision.id})")

print(f"\n📦 Per-agent audit log: {client.config.base_url}/audit?agent_id={agent.agent_id}")
print("✅ school_compass example completed")
