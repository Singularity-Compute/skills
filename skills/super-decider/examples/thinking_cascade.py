"""Answer fast first, then re-ask only the unsure cases with thinking on.

Most items finish in one quick pass; the few low-confidence ones get a short thought before the answer.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

invoices = [
    {"total": "1,240 EUR", "payments": ["400 EUR", "400 EUR", "440 EUR"]},
    {"total": "980 USD", "payments": ["500 USD", "380 USD"]},
    {"total": "75.50 GBP", "payments": ["75.50 GBP"]},
]
QUESTION = {"status": {"type": "choice", "instructions": "Do the `payments` add up to the invoice `total`?",
                       "criteria": {"paid": "Payments add up to the total", "underpaid": "Payments are less than the total",
                                    "overpaid": "Payments are more than the total"}}}
CONFIDENT = 0.9

for inv in invoices:
    first = decide(inv, QUESTION, thinking="off")["status"]
    final, how = first, "fast"
    if first["confidence"] < CONFIDENT:
        final, how = decide(inv, QUESTION, thinking="always")["status"], "with thinking"
    print(f"{final['choice']:9s} {final['confidence']:.2f} ({how}, first pass {first['choice']} {first['confidence']:.2f})  {inv}")
