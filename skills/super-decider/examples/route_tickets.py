"""Route support tickets: pick the team, ask each team's follow-up up front, and send unsure cases to a person.

One request per ticket asks the routing question plus every branch's follow-up (speculative fan-out).
Code reads only the follow-up that matches the chosen team.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

ROUTE_THRESHOLD = 0.75

QUESTIONS = {
    "team": {"type": "choice", "instructions": "Which team should handle this ticket?",
             "criteria": {"billing": "Charges, invoices, refunds, payment methods",
                          "technical": "Errors, outages, something in the product not working",
                          "account": "Login, password, profile, plan changes",
                          "other": "None of these teams"}},
    "billing_refund": {"type": "noul", "instructions": "If this is a billing ticket: does the customer ask for money back?"},
    "technical_severity": {"type": "score", "instructions": "If this is a technical ticket: how badly is the customer blocked?",
                           "criteria": ["Not blocked, a question or a cosmetic issue", "Annoying but has a workaround",
                                        "One important feature unusable", "Cannot use the product at all"]},
    "account_locked_out": {"type": "noul", "instructions": "If this is an account ticket: is the customer unable to sign in?"},
}

tickets = [
    "I was charged twice for my March invoice, please return the extra payment.",
    "The export button gives error 500 since this morning, our whole team is stuck.",
    "I forgot my password and the reset email never arrives.",
    "Do you sponsor student hackathons?",
]

for ticket in tickets:
    a = decide({"ticket": ticket}, QUESTIONS)
    team = a["team"]
    if team["confidence"] < ROUTE_THRESHOLD or team["choice"] == "other":
        print(f"[human review] {team['choice']} ({team['confidence']:.2f}): {ticket}")
        continue
    if team["choice"] == "billing":
        detail = f"refund requested: {a['billing_refund']['noul']:.2f}"
    elif team["choice"] == "technical":
        detail = f"blocked level {a['technical_severity']['score']:.1f} of 3"
    else:
        detail = f"locked out: {a['account_locked_out']['noul']:.2f}"
    print(f"[{team['choice']}] ({team['confidence']:.2f}) {detail}: {ticket}")
