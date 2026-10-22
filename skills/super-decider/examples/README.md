# Examples

Each script is self-contained and uses [`../scripts/decide.py`](../scripts/decide.py). Set `API_KEY` (and `SUPER_DECIDER_URL` for a self-hosted server), then run `python3 examples/<name>.py` from the skill folder.

| Script | Pattern |
|---|---|
| `route_tickets.py` | Routing with speculative follow-up questions and a confidence gate to human review |
| `guardrails.py` | Screening LLM input and output: one yes/no per hazard, block / review / pass in code |
| `rerank.py` | Reranking retrieved passages with one score each, plus an "is it answerable" check |
| `extract_values.py` | Copying values out of text with `span` / `spans`, then validating them in code |
| `verify_claims.py` | Checking claims or citations against a source, with thinking on |
| `composite_score.py` | Scoring a lead on several dimensions and weighting them in code |
| `agent_tool_gate.py` | Deciding whether an agent's proposed tool call runs, asks the user first, or is refused |
| `model_router.py` | Sending each request to the cheapest LLM that can handle it |
| `multilabel_moderation.py` | Labels that can apply together: one yes/no per label |
| `thinking_cascade.py` | A fast pass for everything, a second pass with thinking only for unsure items |
