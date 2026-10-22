"""Check claims against their source before showing them, for example citations in a RAG answer.

Each claim gets one choice: supported, contradicted, or not mentioned by the source.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from decide import decide

source = ("The Eiffel Tower was completed in March 1889 for the World's Fair. It is 330 metres tall "
          "including antennas and was the tallest man-made structure in the world until 1930.")
claims = [
    "The Eiffel Tower was finished in 1889.",
    "The tower is 450 metres tall.",
    "Gustave Eiffel lived in an apartment at the top of the tower.",
]
VERDICT = {"supported": "The source states this", "contradicted": "The source states something incompatible",
           "not_mentioned": "The source does not say either way"}

questions = {f"claim_{i}": {"type": "choice", "criteria": VERDICT,
                            "instructions": f"Compare `claims[{i}]` with `source`. What does the source say about it?"}
             for i in range(len(claims))}
a = decide({"source": source, "claims": claims}, questions, thinking="always")
for i, claim in enumerate(claims):
    v = a[f"claim_{i}"]
    print(f"{v['choice']:13s} {v['confidence']:.2f}  {claim}")
