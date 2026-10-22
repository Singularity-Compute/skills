---
name: super-decider
description: Builds software features on Super Decider, a decision model that returns typed answers (choice, yes/no, score, text spans) with calibrated probabilities instead of generated text. Use when code needs a semantic judgment such as routing tickets, classifying intents, moderating content, gating an agent's tool call, reranking or filtering passages, checking a document against a policy, or extracting a value from text, and whenever code calls an LLM only to pick a label or parse a yes/no out of its reply. Also use when migrating from Jev or the TypeSafe System One API. Not for generating prose, summaries or chat replies.
license: Apache-2.0
compatibility: Needs network access to https://llm.a.singularitycompute.com (or a self-hosted server) and an API key in the API_KEY environment variable.
metadata:
  version: 0.1.0
  homepage: https://github.com/Singularity-Compute/super-decider
---

# Build with Super Decider

Super Decider answers typed questions about a state. You send the state (text, JSON or up to 8 images) and a set of questions with fixed answers; it returns, per question, the chosen answer and a probability for every option. It never writes prose, so your code consumes the answer directly. Your code stays in charge of the flow and calls the model only for the judgment it cannot make itself.

Its API is compatible with TypeSafe's System One API (Jev), plus two extras: `span`/`spans` questions that copy text out of the state, and per-request control of thinking.

## When to use it, and when not

Use it where a program needs semantic understanding at a decision point:

- pick one of known options: route a ticket, choose a handler or tool, label an intent
- check a condition: is this phishing, does the reply follow the policy, should the agent ask first
- rate along a described scale: urgency, severity, relevance of a passage
- copy a value out of text: an order number, a date phrase, the clause that answers a question

Keep these in ordinary code instead: exact lookups, arithmetic, date math, regex-able formats, rules you can already write down, and anything that must produce new text. When a task needs free-form writing, use an LLM and let Super Decider decide whether and where to call it.

## Workflow

1. **Start from the outcome.** Name the decision points in the feature: where the code branches, filters, ranks or escalates. Each decision point becomes one or more questions.
2. **Design the questions.** Pick the type by what the answer means (table below). Read [references/question-design.md](references/question-design.md) before writing instructions and criteria for anything non-trivial.
3. **Build the state.** Give every question the evidence it needs: the text, the record, the policy, relevant facts. Prefer a JSON object with named fields over one long string when the context has parts.
4. **Batch.** Put every independent question about the same state into one request. One pass answers all of them, each on its own: no question gets to read another's answer.
5. **Decide in code.** Read probabilities and confidence, apply thresholds, and route uncertain cases to a person, a retry with thinking, or a larger model. See [references/patterns.md](references/patterns.md) for worked patterns.
6. **Check before shipping.** Validate request bodies with `python3 "${CLAUDE_SKILL_DIR}/scripts/check_request.py" request.json`, send one with `scripts/decide.py`, then test representative cases from the user's data and tune thresholds on them.

## Question types

| Need | Type | Criteria | Answer |
|---|---|---|---|
| One option from a set | `choice` | object: option name -> description or `null` | `choice`, `probabilities`, `confidence` |
| Whether a condition holds | `noul` | optional `{"true": ..., "false": ...}` | `noul` = probability of yes (no `confidence` field) |
| Position on ordered levels | `score` | list of levels, lowest first | `score` = expected level index (0-based float), `legend`, `probabilities`, `confidence` |
| One piece of the state's text | `span` | optional `{"max_tokens": n}` | `found`, `text`, `start`, `end`, `confidence` |
| Every matching piece | `spans` | optional `{"max_tokens": n, "max_items": n}` | `found`, `items` |

When several labels can apply at once, ask one `noul` per label instead of one `choice`. Give a `choice` a no-match option (`"none"`, `"other"`) whenever nothing may fit, because the model must pick one of the options you list.

## Minimal call

```bash
curl https://llm.a.singularitycompute.com/v1/systemone \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "super-decider",
       "state": {"ticket": "I was charged twice for my March invoice."},
       "questions": {
         "team": {"type": "choice", "instructions": "Which team should handle this ticket?",
                  "criteria": {"billing": "Payments, invoices, refunds", "technical": "Bugs and outages",
                               "account": "Login and profile", "other": "None of these"}},
         "urgent": {"type": "noul", "instructions": "Does the customer need an answer today?"}}}'
```

Python helper without dependencies: [scripts/decide.py](scripts/decide.py) (import `decide(state, questions, **options)` or run it on a JSON file). The same endpoint serves OpenAI chat completions; see [references/api.md](references/api.md) for that format, images, limits and errors.

## Thinking

By default (`"thinking": "auto"`) the model answers in one pass and adds a short thought only on uncertain questions, for text requests with at most 2 questions, and only when the server is not busy. Set `"thinking": "always"` when answers need a calculation, a date comparison or several reasoning steps; it costs about 0.5 to 2 s more per request. Set `"thinking": "off"` for pure classification on the hot path. `"auto_forced"` behaves like `auto` but is not skipped under load.

A useful cascade: ask without thinking, then re-ask only the low-confidence items with `"thinking": "always"`.

## Using probabilities

- Thresholds belong in code and depend on the cost of a mistake. Start from the user's data, not from a fixed number.
- `confidence` of a `choice` or `score` is the probability of the top answer. It says how concentrated the distribution is, not whether the whole workflow is right.
- Low confidence can mean two options are both acceptable. Check which options compete before treating it as an error.
- A `score` is an expected value: 1.4 on a 0 to 2 scale means "between medium and high, closer to medium". Use `probabilities` when you need the most likely level.
- Ignore uncertainty on answers your code will not use (for example, speculative branches that did not apply).

## Gotchas

- `model` is required and must be `super-decider`. A missing or unknown model returns 400.
- Question ids appear in the prompt, so name them meaningfully (`refund_eligible`, not `q3`), but put the full meaning in `instructions`.
- Option names are shown next to their descriptions. Use readable names and say what each option covers.
- Score levels should each describe a concrete situation that stands on its own, not just "1", "2", "3".
- More than 26 options in one `choice` works (tested up to 151) but is read in chunks and is slower. Pre-filter in code when you can.
- Up to 64 questions and 131,072 tokens per request. Extra questions are cheap but not free: measure tokens and latency on real requests.
- Typed output guarantees the shape of the answer, not its truth. Validate on the user's domain before automating a decision that matters.
- Keep the API key server-side. In web apps call Super Decider from the backend.

## References

- [references/api.md](references/api.md): endpoints, request and answer fields, thinking options, images, chat completions, limits, errors, self-hosting
- [references/question-design.md](references/question-design.md): writing state, instructions, criteria and levels, with good and weak examples
- [references/patterns.md](references/patterns.md): routing, confidence gating, guardrails, reranking, extraction, verification, composite scoring, agent tool gating, cascades
- [references/migrate-from-jev.md](references/migrate-from-jev.md): moving an existing Jev or TypeSafe integration
- [examples/](examples/): runnable Python examples for the patterns (`python3 examples/<name>.py` with `API_KEY` set)
