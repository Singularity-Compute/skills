---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

Our support inbox gets tickets as plain text. Write a Python function `route(ticket: str) -> dict` in `router.py` that uses Super Decider to decide which team gets the ticket (billing, technical, account) and sends it to a human when the model is not sure. The API key is in the API_KEY environment variable. Don't run it, just write the code.
