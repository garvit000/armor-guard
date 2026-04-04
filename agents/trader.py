"""
Trader Agent — ArmorGuard AI
============================
Live production execution layer via pure python requests
to avoid SDK dependency conflicts on Vercel.
"""

import os
import sys
import requests
from datetime import datetime, timezone

# Add parent to path for core import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.db import SessionLocal, TradeLog

def execute(intent: dict, market_data: dict) -> dict:
    """
    Submit live order execution to Alpaca REST APIs and persist receipt to DB.
    """
    key_id = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_API_SECRET", "")
    
    if not key_id or not secret_key or key_id == "your_alpaca_api_key_here":
        raise Exception("ALPACA API KEYS Missing. Cannot execute production trade.")

    ticker = intent["ticker"]
    qty = intent["qty"]
    action_str = intent["action"].lower()
    
    headers = {
        "APCA-API-KEY-ID": key_id,
        "APCA-API-SECRET-KEY": secret_key,
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = {
        "symbol": ticker,
        "qty": str(qty),
        "side": action_str,
        "type": "market",
        "time_in_force": "gtc"
    }
    
    try:
        url = "https://paper-api.alpaca.markets/v2/orders"
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code not in (200, 201):
            raise Exception(f"Alpaca Rejected Execution: {response.text}")
            
        order = response.json()
    except Exception as e:
        raise Exception(f"Execution Error: {str(e)}")

    alpaca_order_id = str(order["id"])
    status = order["status"].upper()
    price = market_data.get("price", 0.0) 
    notional = round(price * qty, 2)
    
    session = SessionLocal()
    try:
        log_entry = TradeLog(
            order_id=alpaca_order_id,
            ticker=ticker,
            action=action_str.upper(),
            qty=qty,
            fill_price=price,
            notional=notional,
            status=status
        )
        session.add(log_entry)
        session.commit()
    finally:
        session.close()

    return {
        "order_id": alpaca_order_id,
        "status": status,
        "ticker": ticker,
        "action": action_str.upper(),
        "qty": qty,
        "fill_price": price,
        "notional": notional,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "broker": "Alpaca Paper (Production REST)"
    }
