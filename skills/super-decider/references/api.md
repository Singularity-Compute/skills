# Super Decider API reference

Contents: endpoints and auth · request body · answers · thinking · chat completions · images · limits · errors · self-hosting

## Endpoints and auth

Base URL: `https://llm.a.singularitycompute.com` (hosted). A self-hosted server listens on `http://localhost:8011` by default.

| Method and path | Use |
|---|---|
| `POST /v1/systemone` | Typed decisions in the System One (Jev) request shape |
| `POST /v1/chat/completions` | The same decisions through the OpenAI chat completions shape |
| `GET /v1/models` | Lists models; Super Decider appears as `super-decider` |

Every hosted request needs `Authorization: Bearer <key>` and `"model": "super-decider"` in the body. Keys come from ASI:Cloud (https://asicloud.cudos.org/). Read the key from an environment variable and keep it on the server side.

## Request body (`/v1/systemone`)

| Field | Required | Meaning |
|---|---|---|
| `model` | yes | `"super-decider"` |
| `state` | yes | What the questions are about: a string, a JSON object or an array |
| `questions` | yes | Object mapping a question id to a question |
| `images` | no | Up to 8 images as `data:image/...;base64,...` URLs, read together with the state |
| `instructions` | no | Context that applies to every question (for example a policy) |
| `thinking` | no | `"off"`, `"auto"` (default), `"auto_forced"` or `"always"` |
| `thinking_budget` | no | Thought length in tokens, 16 to 4096 (default 512) |

A question is `{"type": ..., "instructions": ..., "criteria": ...}`:

```json
{
  "team":     {"type": "choice", "instructions": "Which team should handle this ticket?",
               "criteria": {"billing": "Payments and refunds", "technical": "Bugs and outages", "other": null}},
  "urgent":   {"type": "noul", "instructions": "Does the customer need an answer today?",
               "criteria": {"true": "A deadline, an outage or money at risk today", "false": "Can wait for normal handling"}},
  "severity": {"type": "score", "instructions": "How much is the customer affected?",
               "criteria": ["Not affected", "Minor inconvenience", "Cannot use one feature", "Cannot use the product"]},
  "order_id": {"type": "span", "instructions": "The order number the customer refers to"},
  "products": {"type": "spans", "instructions": "Every product name mentioned", "criteria": {"max_items": 10}}
}
```

- `choice` criteria: option name to description, or to `null` when the name says enough. At least 2 options.
- `noul` criteria: optional descriptions of what counts as yes (`"true"`) and no (`"false"`).
- `score` criteria: ordered list of levels, lowest first, at least 2.
- `span` / `spans` criteria: optional `max_tokens` (1 to 96) and, for `spans`, `max_items` (1 to 64, default 16). The answer is always copied verbatim from the state's text.

## Answers

```json
{"model": "super-decider",
 "answers": {
   "team":     {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.96, "technical": 0.03, "other": 0.01}, "confidence": 0.96},
   "urgent":   {"type": "noul", "noul": 0.12},
   "severity": {"type": "score", "score": 1.2, "legend": {"0": "Not affected", "1": "Minor inconvenience", "2": "...", "3": "..."},
                "probabilities": {"0": 0.05, "1": 0.70, "2": 0.25, "3": 0.0}, "confidence": 0.70}},
 "usage": {"input_tokens": 312, "output_tokens": 24}}
```

- `choice`: the picked option, a probability per option (they sum to 1) and `confidence` (the top probability).
- `noul`: probability that the answer is yes. There is no `confidence` field.
- `score`: probability-weighted level index (0-based float), the `legend`, a probability per level and `confidence` (the top level's probability).
- `span`: `found`, `text`, `start`, `end` (character offsets into a string state, or into its `"text"` field when the state is an object), `confidence`.
- `spans`: `found` and `items`, each with `text`, `start`, `end`, `confidence`.
- `usage`: real token counts; `output_tokens` includes any thought.

## Thinking

| Value | Behavior | Use for |
|---|---|---|
| `"off"` | One pass, no thought | Hot-path classification |
| `"auto"` (default) | A short thought only on uncertain questions; skipped when the server is busy | General use |
| `"auto_forced"` | Like `auto`, never skipped under load | Batch jobs where accuracy matters more than latency |
| `"always"` | Every question gets a thought first | Calculations, dates, multi-step policy checks |

`auto` and `auto_forced` think only on text requests with at most 2 questions. Requests with images or more questions think only with `"always"`. The thought is not returned. Thinking adds about 0.5 to 2 s.

## Chat completions (`/v1/chat/completions`)

Send exactly two messages: a `system` message whose content is the question schema as JSON, and a `user` message whose content is the state, also as JSON (wrap a plain string with `json.dumps`). Plain chat text returns 400.

```python
import json, os
from openai import OpenAI

client = OpenAI(base_url="https://llm.a.singularitycompute.com/v1", api_key=os.environ["API_KEY"])
schema = {"questions": [
    {"id": "intent", "type": "choice", "instructions": "What does the user want?",
     "options": [{"name": "refund", "description": "Money back"}, {"name": "track", "description": "Where an order is"},
                 {"name": "other", "description": "Anything else"}]},
    {"id": "angry", "type": "noul", "instructions": "Is the user angry?"},
    {"id": "effort", "type": "score", "instructions": "How much work will this take?", "levels": ["minutes", "hours", "days"]},
]}
r = client.chat.completions.create(model="super-decider", messages=[
    {"role": "system", "content": json.dumps(schema)},
    {"role": "user", "content": json.dumps("Tracking hasn't moved in five days and nobody answers my emails.")},
])
answers = json.loads(r.choices[0].message.content)["answers"]
```

In this format every answer also carries a ready `label` (for `noul`: `"yes"` or `"no"`, with `confidence` and `probabilities`).

Chat completions ignore the `thinking` field. Control thinking with keys in the schema JSON instead: `"adaptive": false` turns the automatic thought off (like `"thinking": "off"`), and `"think": 512` gives every question a thought of up to 512 tokens (like `"thinking": "always"`). Without either key the server behaves like `"auto"`.

```python
schema = {"think": 512, "questions": [...]}   # reason through every question
schema = {"adaptive": False, "questions": [...]}  # fastest: no thought
```

## Images

Put up to 8 images in an `images` array of base64 data URLs next to `state`. Multipart uploads are not supported on the hosted API. In chat completions, the `user` content is a list of `image_url` parts plus an optional text part. The model was not fine-tuned on images: test image questions on your own data.

## Limits

- 131,072 tokens per request, up to 64 questions, up to 8 images.
- `choice` with more than 26 options works (tested up to 151); it is read in chunks and takes longer.
- Typical latency about 0.25 s per request without thinking over the internet, about 0.1 s from the same data centre.
- Requests are rate-limited per key.

## Errors

| Status | When | Body |
|---|---|---|
| 400 | `model` missing | `{"error": "Model name not provided"}` |
| 400 | unknown `model` name | `{"error": "Model not found"}` |
| 400 / 422 | invalid request: unknown `thinking` value, bad question shape, state too long | `{"error": {"code": ..., "message": "<server error as a JSON string>"}}` |
| 401 | no `Authorization` header, or not `Bearer sk-...` | `{"error": {"code": "authentication_error", ...}}` |
| 403 | key not valid | `{"error": {"code": "authentication_error", "message": "Access forbidden"}}` |
| 429 | rate limit for the key | no `Retry-After` header; wait a second or two and retry |

The `message` of a validation error is itself JSON; parse it to read the reason, for example `thinking: one of "off", "auto", "auto_forced", "always"`.

## Self-hosting

The runtime is open: https://github.com/Singularity-Compute/super-decider (Docker image, vLLM patches, server). It needs one 48 GB GPU (tested on L40S) and serves the same API on port 8011. Set `API_KEY` on the server to require a bearer token; without it the server accepts unauthenticated requests. Weights: https://huggingface.co/Singularity-Compute/super-decider
