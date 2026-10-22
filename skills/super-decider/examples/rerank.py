"""Rerank retrieved passages for a query and check whether any of them answers it.

One request scores every passage (one score question per passage) and asks one yes/no about the whole set.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

query = "How long do I have to return an item bought online?"
passages = [
    "Store hours are 9:00 to 21:00 on weekdays and 10:00 to 18:00 on weekends.",
    "Online purchases can be returned within 30 days of delivery for a full refund.",
    "Gift cards cannot be exchanged for cash and do not expire.",
    "Items bought in a physical store can be exchanged within 14 days with the receipt.",
]
LEVELS = ["Unrelated to the query", "Related topic but does not answer it", "Partly answers it", "Directly answers it"]

questions = {f"passage_{i}": {"type": "score", "criteria": LEVELS,
                              "instructions": f"How well does `passages[{i}]` answer `query`?"}
             for i in range(len(passages))}
questions["answerable"] = {"type": "noul", "instructions": "Does any of `passages` answer `query`?"}

a = decide({"query": query, "passages": passages}, questions)
ranked = sorted(range(len(passages)), key=lambda i: a[f"passage_{i}"]["score"], reverse=True)
print(f"answerable: {a['answerable']['noul']:.2f}")
for i in ranked:
    print(f"{a[f'passage_{i}']['score']:.2f}  {passages[i]}")
