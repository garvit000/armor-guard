"""
Policy Engine — ArmorGuard AI
==============================
Deterministic rule-based policy engine that gates every parsed intent
before it reaches the trade-execution layer.

Rules
-----
1. Only whitelisted tickers may be traded.
2. Maximum quantity per single trade is capped.
3. Action must be a recognised verb (BUY / SELL).
"""

from dataclasses import dataclass, field
from typing import List

# ── Configuration ─────────────────────────────────────────────────────
ALLOWED_TICKERS: List[str] = ["NVDA", "AAPL", "MSFT"]
MAX_QTY_PER_TRADE: int = 2
ALLOWED_ACTIONS: List[str] = ["BUY", "SELL"]


@dataclass
class PolicyResult:
    """Immutable result returned by the policy check."""
    allowed: bool
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reasons": self.reasons,
        }


def evaluate(intent: dict) -> PolicyResult:
    """
    Evaluate a parsed intent against the policy rule-set.

    Parameters
    ----------
    intent : dict
        Must contain keys ``ticker``, ``qty``, ``action``.

    Returns
    -------
    PolicyResult
        ``.allowed`` is True only when *every* rule passes.
    """
    violations: List[str] = []

    # Rule 0 – intent must have parsed successfully
    if "error" in intent:
        return PolicyResult(allowed=False, reasons=[intent["error"]])

    ticker = intent.get("ticker", "")
    qty = intent.get("qty", 0)
    action = intent.get("action", "")

    # Rule 1 – ticker whitelist
    if ticker not in ALLOWED_TICKERS:
        violations.append(
            f"Ticker '{ticker}' is not in the allowed list "
            f"({', '.join(ALLOWED_TICKERS)})."
        )

    # Rule 2 – quantity cap
    if qty > MAX_QTY_PER_TRADE:
        violations.append(
            f"Quantity {qty} exceeds the maximum allowed per trade "
            f"({MAX_QTY_PER_TRADE})."
        )

    # Rule 3 – valid action
    if action not in ALLOWED_ACTIONS:
        violations.append(
            f"Action '{action}' is not recognised. "
            f"Allowed actions: {', '.join(ALLOWED_ACTIONS)}."
        )

    if violations:
        return PolicyResult(allowed=False, reasons=violations)

    return PolicyResult(
        allowed=True,
        reasons=["All policy checks passed."],
    )


# ── Quick smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        {"ticker": "NVDA", "qty": 1, "action": "BUY"},
        {"ticker": "NVDA", "qty": 100, "action": "BUY"},
        {"ticker": "TSLA", "qty": 1, "action": "BUY"},
    ]
    for s in samples:
        r = evaluate(s)
        tag = "✅ ALLOWED" if r.allowed else "🚫 BLOCKED"
        print(f"{s} → {tag} — {r.reasons}")
