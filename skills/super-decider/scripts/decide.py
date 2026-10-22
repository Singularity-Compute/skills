#!/usr/bin/env python3
"""Call Super Decider's /v1/systemone endpoint. Standard library only.

As a module:
    from decide import decide
    answers = decide({"ticket": "..."}, {"team": {"type": "choice", ...}}, thinking="off")

As a command (prints the full response; exits 1 with the server's message on an HTTP error):
    python3 decide.py request.json          # a file with {"state": ..., "questions": ...}
    echo '{...}' | python3 decide.py -

Environment: API_KEY (required for the hosted API), SUPER_DECIDER_URL (default https://llm.a.singularitycompute.com).
"""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = "https://llm.a.singularitycompute.com"


class DecideError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body}")
        self.status, self.body = status, body


def call(body, timeout=120):
    """POST a full request body; returns the parsed response."""
    body = {"model": "super-decider", **body}
    headers = {"Content-Type": "application/json"}
    if os.environ.get("API_KEY"):
        headers["Authorization"] = "Bearer " + os.environ["API_KEY"]
    url = os.environ.get("SUPER_DECIDER_URL", DEFAULT_URL).rstrip("/") + "/v1/systemone"
    req = urllib.request.Request(url, json.dumps(body).encode(), headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise DecideError(e.code, e.read().decode(errors="replace")) from None


def decide(state, questions, **options):
    """Ask questions about a state; returns the answers object keyed by question id.

    options: thinking ("off" | "auto" | "auto_forced" | "always"), thinking_budget, instructions, images.
    """
    return call({"state": state, "questions": questions, **options})["answers"]


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    text = sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read()
    try:
        print(json.dumps(call(json.loads(text)), indent=2, ensure_ascii=False))
    except DecideError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
