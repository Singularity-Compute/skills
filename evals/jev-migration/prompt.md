---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Here is our current code:

```python
import os, requests
def is_urgent(text):
    r = requests.post("https://api.typesafe.ai/v1/systemone",
        headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"},
        json={"model": "jev-latest", "state": text,
              "questions": {"urgent": {"type": "noul", "instructions": "Is this urgent?"}}})
    return r.json()["answers"]["urgent"]["noul"] > 0.5
```

Move it to Super Decider. Write the new version to `urgent.py` and tell me what else I should check.
