"""
Trader Agent — ArmorGuard AI
============================
Simulated Alpaca execution logic with stop-loss/take-profit mockup
and database persistence.
"""

import uuid
from datetime import datetime, timezone
import os
import sys

# Add parent to path for core import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db import SessionLocal, TradeLog

def execute(intent: dict, market_data: dict) -> dict:
    """
    Execute trade and persist to DB.
    """
    ticker = intent["ticker"]
    qty = intent["qty"]
    action = intent["action"]
    
    # Use real price if available, else fallback
    price = market_data.get("price", 100.0)
    notional = round(price * qty, 2)
    order_id = "AMR-" + str(uuid.uuid4())[:8].upper()
    
    # Create DB entry
    session = SessionLocal()
    try:
        log_entry = TradeLog(
            order_id=order_id,
            ticker=ticker,
            action=action,
            qty=qty,
            fill_price=price,
            notional=notional,
            status="FILLED"
        )
        session.add(log_entry)
        session.commit()
    finally:
        session.close()

    return {
        "order_id": order_id,
        "status": "FILLED",
        "ticker": ticker,
        "action": action,
        "qty": qty,
        "fill_price": price,
        "notional": notional,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "broker": "Alpaca Paper (Simulated)"
    }
