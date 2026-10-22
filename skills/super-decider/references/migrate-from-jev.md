# Moving from Jev (TypeSafe System One API)

Super Decider accepts the System One request shape, so most Jev integrations move by changing two values.

## Change

| Setting | Jev | Super Decider |
|---|---|---|
| Endpoint | `https://api.typesafe.ai/v1/systemone` (or a gateway such as OpenRouter) | `https://llm.a.singularitycompute.com/v1/systemone` |
| `model` | `jev-latest`, `jev-1.14.0`, `typesafe/jev-1.13` | `super-decider` (any other name returns 400) |
| Key | TypeSafe or OpenRouter key | Super Decider key from ASI:Cloud, as `Authorization: Bearer ...` |

`state`, `questions`, `noul` / `choice` / `score`, criteria shapes, structured (JSON) instructions and criteria, and the answer fields (`noul`, `choice`, `probabilities`, `confidence`, `score`, `legend`) stay the same.

## Differences to check

- **Images.** Jev uses an `assets` map referenced from the request behind an opt-in header. Super Decider takes an `images` array of base64 data URLs next to `state` (up to 8), with no header.
- **Box questions.** The `box` type from Jev 1.14 is not supported; it returns 422.
- **Extra question types.** `span` and `spans` copy text out of the state with offsets. They can replace pre-parsed value extraction where candidates are hard to find with code.
- **Thinking.** Jev has no thinking control. Super Decider answers in one pass by default and adds a short thought on uncertain text questions; `"thinking": "always"` reasons through every question and `"off"` disables it.
- **Limits.** 131,072 tokens per request and up to 64 questions. `choice` with more than 26 options is read in chunks and is slower; `score` accepts more than 10 levels.
- **Usage.** `usage` reports `input_tokens` and `output_tokens`; there is no `cost` field. Price: $0.03 per million input tokens, output free.
- **SDKs.** TypeSafe's SDKs target TypeSafe's endpoint. With Super Decider, call the HTTP API directly (see `scripts/decide.py`) or use the OpenAI SDK through chat completions.

## Re-check after switching

Different models are calibrated differently. Re-run the integration's test cases and re-tune any confidence thresholds on your own data before relying on the old values.
