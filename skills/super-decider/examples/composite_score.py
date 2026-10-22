"""Score a sales lead on separate dimensions and combine them with weights you control in code.

Changing weights or thresholds later does not need new model calls: the per-dimension answers are reusable data.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

lead = {"company": "Northwind Logistics, 400 employees",
        "message": "We route about 20k support emails a month and our LLM bill is getting out of hand. "
                   "Looking to switch something in the next quarter. Can we get a call with an engineer?",
        "source": "pricing page form"}

DIMENSIONS = {
    "fit": ("How well does the company fit a product that automates decisions in support and operations?",
            ["No fit", "Weak fit", "Good fit", "Ideal fit"]),
    "need": ("How clearly does the lead describe a problem the product solves?",
             ["No problem stated", "Vague interest", "Clear problem", "Clear problem with numbers"]),
    "timing": ("How soon does the lead want to act?",
               ["No timeline", "Someday", "This year", "This quarter or sooner"]),
}
WEIGHTS = {"fit": 0.4, "need": 0.35, "timing": 0.25}

a = decide(lead, {name: {"type": "score", "instructions": text, "criteria": levels}
                  for name, (text, levels) in DIMENSIONS.items()})
normalized = {name: a[name]["score"] / (len(DIMENSIONS[name][1]) - 1) for name in DIMENSIONS}
total = sum(WEIGHTS[n] * normalized[n] for n in DIMENSIONS)
for n in DIMENSIONS:
    print(f"{n:7s} {normalized[n]:.2f}")
print(f"lead score {total:.2f} -> {'sales call' if total >= 0.7 else 'nurture email'}")
