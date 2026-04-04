"""
Trader Agent — ArmorGuard AI
============================
Live production execution layer. Plugs authenticated valid Intent-Tokens
into the real Alpaca Paper Trading API.
"""

import os
import traceback
import sys
from datetime import datetime, timezone
import alpaca_trade_api as tradeapi

# Add parent to path for core import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db import SessionLocal, TradeLog

def execute(intent: dict, market_data: dict) -> dict:
    """
    Submit live order execution to Alpaca APIs and persist receipt to DB.
    """
    key_id = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_API_SECRET", "")
    
    if not key_id or not secret_key or key_id == "your_alpaca_api_key_here":
        raise Exception("ALPACA API KEYS Missing. Cannot execute production trade.")

    ticker = intent["ticker"]
    qty = intent["qty"]
    action_str = intent["action"].lower() # 'buy' or 'sell'
    
    api = tradeapi.REST(key_id, secret_key, base_url='https://paper-api.alpaca.markets', api_version='v2')
    
    # Send actual API command
    try:
        order = api.submit_order(
            symbol=ticker,
            qty=qty,
            side=action_str,
            type='market',
            time_in_force='gtc' # Good till cancel
        )
    except Exception as e:
        raise Exception(f"Alpaca Rejected Execution: {str(e)}")

    alpaca_order_id = str(order.id)
    price = market_data.get("price", 0.0) # Best estimate if not filled immediately
    notional = round(price * qty, 2)
    
    # Create DB entry logging the REAL order id
    session = SessionLocal()
    try:
        log_entry = TradeLog(
            order_id=alpaca_order_id,
            ticker=ticker,
            action=action_str.upper(),
            qty=qty,
            fill_price=price,
            notional=notional,
            status=order.status.upper()
        )
        session.add(log_entry)
        session.commit()
    finally:
        session.close()

    return {
        "order_id": alpaca_order_id,
        "status": order.status.upper(),
        "ticker": ticker,
        "action": action_str.upper(),
        "qty": qty,
        "fill_price": price,
        "notional": notional,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "broker": "Alpaca Paper (Production)"
    }
