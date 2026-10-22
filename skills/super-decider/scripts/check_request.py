#!/usr/bin/env python3
"""Check a Super Decider /v1/systemone request body offline, before sending it.

    python3 check_request.py request.json      # or "-" for stdin

Prints one line per problem and exits 1 if any are errors; warnings alone exit 0.
Checks shapes and limits that the server enforces, plus common design mistakes.
"""
import json
import sys

TYPES = {"choice", "noul", "score", "span", "spans"}
THINKING = {"off", "auto", "auto_forced", "always"}
MAX_QUESTIONS = 64
MAX_IMAGES = 8
NO_MATCH = {"other", "none", "unclear", "unknown", "no_match", "not_applicable", "n/a", "neither"}


def check(body):
    errors, warnings = [], []
    if not isinstance(body, dict):
        return ["request body must be a JSON object"], []
    if body.get("model", "super-decider") != "super-decider":
        errors.append(f'model must be "super-decider", got {body.get("model")!r}')
    if "state" not in body:
        errors.append("state is required")
    qs = body.get("questions")
    if not isinstance(qs, dict) or not qs:
        errors.append("questions must be a non-empty object mapping ids to questions")
        qs = {}
    if len(qs) > MAX_QUESTIONS:
        errors.append(f"at most {MAX_QUESTIONS} questions per request, got {len(qs)}")
    if "thinking" in body and body["thinking"] not in THINKING:
        errors.append(f"thinking must be one of {sorted(THINKING)}")
    tb = body.get("thinking_budget")
    if tb is not None and (isinstance(tb, bool) or not isinstance(tb, int) or not 16 <= tb <= 4096):
        errors.append("thinking_budget must be an integer from 16 to 4096")
    images = body.get("images") or []
    if len(images) > MAX_IMAGES:
        errors.append(f"at most {MAX_IMAGES} images, got {len(images)}")
    for i, im in enumerate(images):
        if isinstance(im, str) and not im.startswith("data:image/"):
            warnings.append(f"images[{i}]: hosted API expects a data:image/...;base64 URL")

    for qid, q in qs.items():
        where = f"question {qid!r}"
        if not isinstance(q, dict):
            errors.append(f"{where}: must be an object")
            continue
        kind = q.get("type")
        if kind not in TYPES:
            errors.append(f"{where}: type must be one of {sorted(TYPES)}, got {kind!r}")
            continue
        if not str(q.get("instructions") or "").strip():
            errors.append(f"{where}: instructions are required")
        crit = q.get("criteria")
        if kind == "choice":
            if not isinstance(crit, dict) or len(crit) < 2:
                errors.append(f"{where}: choice criteria must map at least 2 option names to descriptions or null")
            else:
                if len(crit) > 26:
                    warnings.append(f"{where}: {len(crit)} options are read in chunks and are slower; pre-filter in code if you can")
                if not NO_MATCH & {k.lower() for k in crit}:
                    warnings.append(f"{where}: no no-match option (other/none/unclear); add one if nothing may fit")
        elif kind == "noul":
            if crit is not None and (not isinstance(crit, dict) or set(crit) - {"true", "false"}):
                errors.append(f'{where}: noul criteria, if given, are {{"true": ..., "false": ...}}')
        elif kind == "score":
            if not isinstance(crit, list) or len(crit) < 2:
                errors.append(f"{where}: score criteria must be a list of at least 2 levels, lowest first")
            elif all(str(level).strip().isdigit() for level in crit):
                warnings.append(f"{where}: levels are bare numbers; describe what each level means")
        elif kind in ("span", "spans"):
            if crit is not None and not isinstance(crit, dict):
                errors.append(f"{where}: span criteria, if given, are an object with max_tokens / max_items")
            else:
                for key, hi in (("max_tokens", 96), ("max_items", 64)):
                    v = (crit or {}).get(key)
                    if v is not None and (not isinstance(v, int) or not 1 <= v <= hi):
                        errors.append(f"{where}: {key} must be an integer from 1 to {hi}")
        if len(qid) <= 3 or qid.lower().startswith(("q", "question")) and qid[-1:].isdigit():
            warnings.append(f"{where}: id is shown to the model; prefer a descriptive id")
    return errors, warnings


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
    try:
        body = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: not valid JSON: {e}")
        return 1
    errors, warnings = check(body)
    for e in errors:
        print(f"error: {e}")
    for w in warnings:
        print(f"warning: {w}")
    if not errors and not warnings:
        print("ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
