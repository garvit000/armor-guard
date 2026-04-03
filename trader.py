"""
Paper-Trade Executor — ArmorGuard AI
=====================================
Simulates Alpaca-style paper trade execution.  No real money is ever
involved; the module produces a realistic execution log for demo
purposes.
"""

import uuid
from datetime import datetime, timezone

# ── Simulated price book (static for the hackathon demo) ──────────────
_SIMULATED_PRICES = {
    "NVDA": 924.79,
    "AAPL": 178.72,
    "MSFT": 420.55,
}


def execute(intent: dict) -> dict:
    """
    Simulate a paper trade and return an execution log.

    Parameters
    ----------
    intent : dict
        Parsed + policy-approved intent with ``ticker``, ``qty``, ``action``.

    Returns
    -------
    dict
        Execution log containing order id, timestamp, fill price, and
        total notional value.
    """
    ticker = intent["ticker"]
    qty = intent["qty"]
    action = intent["action"]
    price = _SIMULATED_PRICES.get(ticker, 100.00)
    notional = round(price * qty, 2)

    return {
        "order_id": str(uuid.uuid4())[:8],
        "status": "FILLED",
        "ticker": ticker,
        "action": action,
        "qty": qty,
        "fill_price": price,
        "notional": notional,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "broker": "Alpaca Paper",
    }


# ── Quick smoke test ──────────────────────────────────────────────────
if __name__ == "__main__":
    log = execute({"ticker": "NVDA", "qty": 1, "action": "BUY"})
    for k, v in log.items():
        print(f"  {k}: {v}")
