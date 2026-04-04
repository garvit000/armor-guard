"""
Analyst Agent — ArmorGuard AI
==============================
Provides market data and technical indicators.
Mocked for the hackathon demo since real data (yfinance/pandas) 
is blocked by Windows Application Control policies on this system.
"""

import random

def analyze(ticker: str) -> dict:
    """
    Mock market data and compute indicators for a given ticker.
    
    Returns:
        dict: containing price, sma20, sma50, rsi, recommendation, confidence
    """
    # Deterministic mock data for clear demos
    t = ticker.upper()
    
    if t == "NVDA":
        current_price = 924.79
        sma20 = 910.50
        sma50 = 850.25
        rsi = 65.4
        recommendation = "BUY"
        confidence = 80
    elif t == "AAPL":
        current_price = 178.72
        # RSI < 30 case for autonomous trigger demo
        sma20 = 185.10
        sma50 = 190.20
        rsi = 28.5 
        recommendation = "BUY" # Oversal condition
        confidence = 75
    elif t == "MSFT":
        current_price = 420.55
        sma20 = 415.00
        sma50 = 400.00
        rsi = 55.0
        recommendation = "HOLD"
        confidence = 50
    elif t == "TSLA":
        current_price = 175.22
        sma20 = 190.00
        sma50 = 210.00
        rsi = 35.0
        recommendation = "SELL"
        confidence = 60
    else:
        # Fallback random mock
        current_price = round(random.uniform(50, 500), 2)
        sma20 = current_price * 0.95
        sma50 = current_price * 0.90
        rsi = round(random.uniform(20, 80), 2)
        recommendation = "HOLD"
        confidence = 50
        
    return {
        "price": current_price,
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "rsi": round(rsi, 2),
        "recommendation": recommendation,
        "confidence": confidence
    }

if __name__ == "__main__":
    import json
    res = analyze("NVDA")
    print(json.dumps(res, indent=2))
