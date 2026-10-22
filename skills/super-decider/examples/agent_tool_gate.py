"""Gate an agent's tool call: run it, ask the user first, or refuse.

The agent proposes an action; Super Decider judges it against the user's request and a policy before code executes it.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

POLICY = ("The agent may read anything. Sending email, deleting data and spending money need the user's "
          "confirmation unless the user asked for that exact action in this conversation.")

proposals = [
    {"user_request": "Find last week's invoices from Acme.", "tool": "search_files", "args": {"query": "Acme invoice"}},
    {"user_request": "Find last week's invoices from Acme.", "tool": "delete_files", "args": {"query": "Acme invoice"}},
    {"user_request": "Email the Q3 report to Sam.", "tool": "send_email", "args": {"to": "sam@example.com", "attach": "q3.pdf"}},
]
QUESTIONS = {
    "next_step": {"type": "choice", "instructions": "Given `user_request` and `policy`, what should happen with `tool` and `args`?",
                  "criteria": {"run": "Run it now: requested and allowed",
                               "ask_user": "Ask the user to confirm first",
                               "refuse": "Do not run it: not what the user asked for or against the policy"}},
    "matches_request": {"type": "noul", "instructions": "Does the proposed `tool` call do what `user_request` asks?"},
}
for p in proposals:
    a = decide({**p, "policy": POLICY}, QUESTIONS)
    step = a["next_step"]
    print(f"{step['choice']:8s} {step['confidence']:.2f}  matches request {a['matches_request']['noul']:.2f}  {p['tool']}({p['args']})")
