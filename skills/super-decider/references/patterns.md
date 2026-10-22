# Patterns

Contents: 1 routing with fan-out · 2 confidence gating · 3 guardrails · 4 multi-label tagging · 5 reranking and RAG filtering · 6 extraction · 7 verification · 8 composite scoring · 9 agent tool gating · 10 model routing · 11 thinking cascade · 12 hierarchical classification · 13 matching records · 14 deciding what to remember

Runnable versions of patterns 1 to 11 are in [../examples/](../examples/). Each pattern names the shape of the request and what code does with the answers.

## 1. Routing with speculative fan-out

Ask which handler should take a request and, in the same call, each handler's follow-up question. The follow-ups state their premise ("If this is a billing ticket: ..."). Code reads the routing answer and uses only the matching follow-up, so one round trip covers every branch. Example: `examples/route_tickets.py`.

Use a second request only when the follow-up needs evidence you fetch after routing (the customer's invoices, the order history).

## 2. Confidence gating

The answer says what; confidence says whether to act on it. Pick a threshold per action from the cost of a mistake: high for refunds or deletions, lower for tagging. Below it, send the case to a person, ask the user, re-ask with thinking, or fall back to a larger model. Log the answers and outcomes so thresholds can be tuned later without new calls.

## 3. Guardrails for LLM input and output

One request per message, one `noul` per hazard (prompt injection, personal data, abuse, off-topic, unsafe advice). Code maps each hazard to an action and a threshold: block, review, redact, redirect or pass. Screen both directions: what users send to the model and what the model is about to send back. Use `"thinking": "off"` on this hot path. Example: `examples/guardrails.py`.

## 4. Multi-label tagging

When several labels can be true together (spam and insult, spoiler and question), ask one `noul` per label in one request and keep every label above its threshold. A single `choice` would force exactly one. Example: `examples/multilabel_moderation.py`.

## 5. Reranking and RAG filtering

Put the query and the candidates in the state and ask one `score` per candidate with levels like "unrelated / related but does not answer / partly answers / directly answers". Sort by the score float. Add a `noul` "does any passage answer the query?" so code can say "I don't know" instead of answering from weak context. Pre-filter candidates with search (BM25, embeddings) so each request holds tens, not thousands. Example: `examples/rerank.py`.

## 6. Extraction: copy, then validate

Use `span` for one value and `spans` for every occurrence. The text is copied from the state, never generated, and comes with character offsets. Validate the copy in code (format, range, checksum) and normalize it there. When code can find the candidates itself (all emails, all amounts with a regex), list them and ask a `choice` over the candidates instead. Example: `examples/extract_values.py`.

## 7. Verification of claims and citations

For each claim, ask a `choice` over "supported / contradicted / not mentioned" against the source it cites. Show supported claims, flag contradicted ones, and treat "not mentioned" as unsupported. Use `"thinking": "always"` when claims involve numbers, dates or several facts. The same shape checks a draft reply against a policy or an extracted field against its document. Example: `examples/verify_claims.py`.

## 8. Composite scoring

Break a fuzzy judgment ("is this a good lead?", "is this pull request risky?") into separate `score` questions with concrete levels. Combine them in code with weights you can change, and keep the per-dimension answers: changing weights later needs no new calls. Use a separate `noul` for any hard rule ("any serious violation") instead of hoping a weighted sum catches it. Example: `examples/composite_score.py`.

## 9. Agent tool gating

Before an agent runs a tool, send the user's request, the proposed call and the policy as the state, and ask a `choice` of "run / ask the user / refuse", plus a `noul` "does this call do what the user asked?". Execute only "run" above the threshold. This catches actions the user did not ask for, such as deleting when asked to search. Example: `examples/agent_tool_gate.py`.

## 10. Model routing

Ask which model tier can handle a request and whether it needs tools or live data. Route routine work to a small model and the rest to a large one; when the tier answer is unsure, choose the larger model. Super Decider decides; the chosen LLM writes. Example: `examples/model_router.py`.

## 11. Thinking cascade

Ask everything with `"thinking": "off"`. Re-ask only the answers below a confidence threshold with `"thinking": "always"`. Most items finish in one fast pass; the hard ones (sums, dates, multi-step rules) get a short thought. Example: `examples/thinking_cascade.py`.

## 12. Hierarchical classification

For deep taxonomies (product catalogues, industry codes), ask a `choice` over the top level, then a second request over the children of the chosen node. Keep the top two or three branches when their probabilities are close and compare their best leaves. When confidence at a level is low, report the parent category instead of guessing a leaf.

## 13. Matching records

To decide whether two records describe the same entity (products from two catalogues, duplicate customers), ask a `score` "same entity" with levels from "clearly different" to "certainly the same", plus one `noul` per field that might disagree (brand, size, model number). The field answers explain mismatches to a reviewer. Block candidate pairs with cheap code first so only plausible pairs reach the model.

## 14. Deciding what to remember

In assistants with memory, ask after each turn whether it contains a durable fact about the user or the task, and which category it belongs to. Store only what passes, and on later calls put the stored facts into the state. The same shape decides which log lines, tickets or messages are worth keeping.
