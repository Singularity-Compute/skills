"""Send each request to the cheapest model that can handle it.

Super Decider decides; the chosen LLM writes. Unsure cases go to the larger model.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

requests = [
    "Translate 'good morning' into Spanish.",
    "Prove that there are infinitely many primes of the form 4k+3.",
    "Summarize this paragraph in one sentence: The meeting moved to Thursday because the client is travelling.",
    "Design the database schema for a multi-tenant invoicing system with audit history.",
]
QUESTIONS = {
    "tier": {"type": "choice", "instructions": "Which model tier can answer `request` well?",
             "criteria": {"small": "Short, routine task: lookups, translations, rewording, simple summaries",
                          "large": "Needs multi-step reasoning, proofs, design or long careful writing"}},
    "needs_tools": {"type": "noul", "instructions": "Does answering `request` need live data or code execution?"},
}
for r in requests:
    a = decide({"request": r}, QUESTIONS, thinking="off")
    tier = a["tier"]
    model = tier["choice"] if tier["confidence"] >= 0.8 else "large"
    print(f"{model:5s} ({tier['choice']} {tier['confidence']:.2f}) tools {a['needs_tools']['noul']:.2f}  {r}")
