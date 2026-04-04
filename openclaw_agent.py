"""
OpenClaw Intent Parser — ArmorGuard AI
======================================
Uses Google Gemini API to dynamically parse natural language 
trade commands into a strict JSON intent payload.
"""

import os
import json
import re
from typing import Optional

try:
    from google import genai
except Exception:
    genai = None
from dotenv import load_dotenv

load_dotenv()

_ACTION_ALIASES = {
    "buy": "BUY",
    "long": "BUY",
    "sell": "SELL",
    "short": "SELL",
}

_COMPANY_TO_TICKER = {
    "nvidia": "NVDA",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "tesla": "TSLA",
}


def _extract_ticker(command: str) -> Optional[str]:
    for company, ticker in _COMPANY_TO_TICKER.items():
        if company in command.lower():
            return ticker

    candidates = re.findall(r"\b[A-Za-z]{1,5}\b", command)
    for token in candidates:
        upper = token.upper()
        if upper in _ACTION_ALIASES.values():
            continue
        if upper in {"IF", "RSI", "SMA", "SMA20", "SMA50", "AND", "OR", "THE", "SHARES"}:
            continue
        if upper.isalpha() and 1 <= len(upper) <= 5:
            return upper
    return None


def _parse_intent_rules(command: str) -> dict:
    text = command.strip()
    if not text:
        return {"error": "Empty command."}

    lowered = text.lower()
    action = None
    for alias, canonical in _ACTION_ALIASES.items():
        if re.search(rf"\b{alias}\b", lowered):
            action = canonical
            break

    if not action:
        return {"error": "Unable to determine action. Use BUY or SELL."}

    qty_match = re.search(r"\b(\d+)\b", lowered)
    qty = int(qty_match.group(1)) if qty_match else 1
    if qty <= 0:
        return {"error": "Quantity must be greater than 0."}

    ticker = _extract_ticker(text)
    if not ticker:
        return {"error": "Unable to determine ticker symbol."}

    return {
        "action": action,
        "qty": qty,
        "ticker": ticker,
        "parser": "openclaw-rules",
    }


def _parse_intent_llm(command: str, api_key: str) -> dict:
    if genai is None:
        return {"error": "google-genai package unavailable."}

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an intent parser for a financial trading gateway.
    Extract the trade intent from the following command: "{command}"

    Rules:
    - Action MUST be exactly "BUY" or "SELL".
    - Ticker MUST be the stock ticker symbol in uppercase (e.g., AAPL).
    - Qty MUST be an integer representing the volume. If not specified, default to 1.
    - Return ONLY valid JSON, nothing else. DO NOT wrap the json in markdown blocks like ```json.

    Example input: "I want to grab 50 shares of nvidia"
    Output: {{"action": "BUY", "qty": 50, "ticker": "NVDA"}}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip().replace("```json", "").replace("```", "")
    intent = json.loads(text)

    if "action" not in intent or "ticker" not in intent or "qty" not in intent:
        return {"error": "Gemini failed to extract all required fields (action, ticker, qty)."}

    intent["action"] = str(intent["action"]).upper()
    intent["ticker"] = str(intent["ticker"]).upper()
    intent["qty"] = int(intent["qty"])
    intent["parser"] = "openclaw-llm"
    return intent

def parse_intent(command: str) -> dict:
    """
    Parse natural language into a JSON intent.
    { "action": "BUY"|"SELL", "qty": int, "ticker": "AAA" }
    """
    _GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    use_llm = bool(_GEMINI_API_KEY and _GEMINI_API_KEY != "your_gemini_api_key_here")

    try:
        if use_llm:
            llm_result = _parse_intent_llm(command, _GEMINI_API_KEY)
            if "error" not in llm_result:
                return llm_result

        # Guaranteed OpenClaw parsing path when LLM is unavailable or fails.
        return _parse_intent_rules(command)

    except Exception as e:
        rule_result = _parse_intent_rules(command)
        if "error" in rule_result:
            return {"error": f"Intent parsing failed: {str(e)}"}
        return rule_result
