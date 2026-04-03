"""
OpenClaw Intent-Parser Agent
=============================
Simulates an OpenClaw autonomous agent that converts natural-language
trading commands into structured JSON intents.

In a production deployment this module would call the OpenClaw SDK;
here we use deterministic NLP parsing so the demo runs offline with
zero API keys.
"""

import re
from typing import Optional


# ── Supported action verbs ────────────────────────────────────────────
_ACTION_MAP = {
    "buy": "BUY",
    "purchase": "BUY",
    "acquire": "BUY",
    "long": "BUY",
    "sell": "SELL",
    "short": "SELL",
    "dump": "SELL",
    "liquidate": "SELL",
}

# Regex: optional action, quantity, ticker
_PATTERN = re.compile(
    r"(?P<action>" + "|".join(_ACTION_MAP.keys()) + r")"
    r"\s+"
    r"(?P<qty>\d+)"
    r"\s+"
    r"(?P<ticker>[A-Za-z]+)",
    re.IGNORECASE,
)


def parse_intent(user_input: str) -> dict:
    """
    Parse a natural-language trading command into a structured intent.

    Returns
    -------
    dict
        On success:  {"ticker": "NVDA", "qty": 1, "action": "BUY"}
        On failure:  {"error": "Could not parse intent from input."}
    """
    user_input = user_input.strip()
    match = _PATTERN.search(user_input)

    if not match:
        return {"error": "Could not parse intent from input."}

    action_raw = match.group("action").lower()
    qty = int(match.group("qty"))
    ticker = match.group("ticker").upper()

    return {
        "ticker": ticker,
        "qty": qty,
        "action": _ACTION_MAP.get(action_raw, "BUY"),
    }


# ── Quick smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    tests = ["buy 1 NVDA", "sell 5 AAPL", "purchase 2 MSFT", "hello world"]
    for t in tests:
        print(f"{t!r:30s} → {parse_intent(t)}")
