---
type: llm
weight: 1
---

The response writes router.py with a function that calls Super Decider correctly:
- POSTs to https://llm.a.singularitycompute.com/v1/systemone (or chat completions on the same host) with "model": "super-decider" and a Bearer key read from API_KEY
- asks a `choice` question with the three teams as options and a no-match option such as "other"
- uses the answer's `confidence` (or probabilities) with a threshold in code to send unsure tickets to a human
- does not ask the model to generate free text or parse prose
