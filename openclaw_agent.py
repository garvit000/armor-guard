"""
OpenClaw Intent Parser — ArmorGuard AI
======================================
Uses Google Gemini API to dynamically parse natural language 
trade commands into a strict JSON intent payload.
"""

import os
import json
import google.generativeai as genai

from dotenv import load_dotenv
load_dotenv()

def parse_intent(command: str) -> dict:
    """
    Parse natural language into a JSON intent.
    { "action": "BUY"|"SELL", "qty": int, "ticker": "AAA" }
    """
    _GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not _GEMINI_API_KEY or _GEMINI_API_KEY == "your_gemini_api_key_here":
         return {"error": "GEMINI_API_KEY is missing. Production mode requires a real API key."}

    genai.configure(api_key=_GEMINI_API_KEY)

    # Use Gemini 1.5 Flash for fast NLP
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
    
    try:
        response = model.generate_content(prompt)
        # Clean any potential markdown formatting the LLM sneaks in
        text = response.text.strip().replace("```json", "").replace("```", "")
        intent = json.loads(text)
        
        # Ensure mandatory keys
        if "action" not in intent or "ticker" not in intent or "qty" not in intent:
             return {"error": "Gemini failed to extract all required fields (action, ticker, qty)."}
             
        # Normalize
        intent["action"] = str(intent["action"]).upper()
        intent["ticker"] = str(intent["ticker"]).upper()
        intent["qty"] = int(intent["qty"])
        
        return intent

    except Exception as e:
        return {"error": f"LLM Parsing failed: {str(e)}"}
