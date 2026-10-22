# Designing questions

Contents: the state · instructions · choice options · yes/no questions · score levels · spans · splitting and batching · checklist

## The state

The state is everything the model may use. It sees nothing else.

- Include the evidence each question needs: the message, the record, the policy, the dates and amounts that matter.
- Prefer a JSON object with named fields when the context has parts, and refer to fields by name in the instructions.
- Trim what no question needs. Unrelated fields cost tokens and can distract.
- Keep instructions out of the state. The state holds data; the question holds the judgment.
- Put knowledge the model cannot know (your product names, your policy, today's date) into the state or the top-level `instructions`.

Good:

```json
{"ticket": {"subject": "Double charge", "body": "I was charged twice for March."},
 "customer": {"plan": "Pro", "since": "2024-02"},
 "policy": "Refunds for duplicate charges are approved without review."}
```

Weak: one string that mixes the ticket, a CRM dump and the instruction "classify this".

## Instructions

Write one narrow judgment per question, in plain language, as if asking a careful colleague.

- Say what to look at: "Based on `ticket.body`, ..." when the state has several fields.
- Include the decision rule when you have one: "Approve if the request is within 30 days of delivery."
- Avoid double questions ("Is it urgent and about billing?"). Split them.
- Name the question id after its meaning (`refund_eligible`). The id is shown to the model, but the instructions must carry the full meaning on their own.

## Choice options

- Use readable option names; the model sees each name with its description.
- Describe what each option covers when names alone are ambiguous, and say where neighbours differ ("billing: payments and refunds; account: login, plan changes").
- Add a no-match option (`other`, `none`, `unclear`) whenever none may fit. Without it the model has to pick a wrong option, often with high confidence.
- Keep options mutually exclusive. When several can be true at once, ask one `noul` per option instead.
- Over 26 options works but is slower. If code can narrow the set first (by product line, language, previous step), do that.

## Yes/no questions (`noul`)

- Phrase the question so that "yes" is the condition you act on: "Does the message ask for a refund?".
- Add `criteria` with `true`/`false` descriptions when the boundary needs defining: what counts as a threat, what counts as complete.
- The answer is a probability of yes. Compare it with a threshold in code; there is no separate confidence.

## Score levels

- List levels lowest first. Each level should describe a concrete situation that stands on its own.

Good: `["Not affected", "Minor inconvenience, has a workaround", "One feature unusable", "Product unusable or data at risk"]`

Weak: `["1", "2", "3", "4"]` or `["low", "medium", "high"]` without saying what each means.

- `score` is the expected level (a float). For a hard bucket use the level with the highest probability; for ranking use the float.

## Spans

- `span` and `spans` copy text verbatim out of the state, so the result is always a real substring with character offsets.
- Use them to pull an order number, a date phrase, a quoted clause or every product name, then normalize or validate the copy in code.
- Check `found` before using the text. A span question on text that does not contain the answer should come back with `found: false` or low confidence.
- When the candidates are structured (all emails, all amounts), find them with code and ask a `choice` over the candidates instead.

## Splitting and batching

- Split a judgment into independent dimensions when each is useful on its own (topic, urgency, sentiment), and keep together what must be judged together (whether this reply answers this question).
- Ask everything about the same state in one request. Each question is answered independently of the others, so a question must not rely on another question's answer.
- Ask speculative questions up front when cheap: if the next step depends on the intent, ask the intent and each branch's follow-up together and let code use only the relevant answers. State each branch's premise in its instructions ("If this is a refund request, ...").
- Make a second request only when an answer changes the evidence or the options for the next question.

## Checklist

- [ ] Each question asks one judgment and makes sense without the others
- [ ] The state holds all the evidence and nothing irrelevant
- [ ] Every `choice` has a no-match option if nothing may fit
- [ ] Options are mutually exclusive, or replaced by one `noul` per label
- [ ] Score levels describe situations, lowest first
- [ ] Thresholds and actions live in code and were tuned on real examples
