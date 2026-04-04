"""
ArmorIQ Cloud Bridge
====================
Pushes intent plans to ArmorIQ using the official SDK so plans appear in
platform.armoriq.ai Intent Intelligence dashboards.
"""

import os
from typing import Any, Dict
from dotenv import load_dotenv

try:
    from armoriq_sdk import ArmorIQClient
except Exception:
    ArmorIQClient = None

load_dotenv()


def _build_plan(command: str, intent: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
    action = intent.get("action", "UNKNOWN")
    ticker = intent.get("ticker", "UNKNOWN")
    qty = intent.get("qty", 0)

    # Use env overrides when the tenant requires exact onboarded MCP/action names.
    mcp_name = os.getenv("ARMORIQ_MCP", "armorguard-trading-mcp")
    mcp_action = os.getenv("ARMORIQ_MCP_ACTION", "execute_trade")

    return {
        "goal": f"{action} {qty} {ticker} from natural language command",
        "steps": [
            {
                "mcp": mcp_name,
                "action": mcp_action,
                "params": {
                    "action": action,
                    "ticker": ticker,
                    "qty": qty,
                    "price": market_data.get("price"),
                    "raw_command": command,
                },
                "description": "Execute policy-gated trading intent",
            }
        ],
        "metadata": {
            "source": "armor-guard",
            "parser": intent.get("parser", "unknown"),
        },
    }


def submit_intent_plan(command: str, intent: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit an intent plan to ArmorIQ cloud and request an intent token.
    Returns a status dict that is safe to include in API responses/audits.
    """
    api_key = os.getenv("ARMORIQ_API_KEY", "")
    user_id = os.getenv("ARMORIQ_USER_ID", "local-user")
    agent_id = os.getenv("ARMORIQ_AGENT_ID", "armor-guard-gateway")

    if ArmorIQClient is None:
        return {
            "enabled": False,
            "success": False,
            "reason": "armoriq-sdk package is not installed",
        }

    if not api_key or api_key == "your_armoriq_api_key_here":
        return {
            "enabled": False,
            "success": False,
            "reason": "ARMORIQ_API_KEY is missing",
        }

    try:
        client = ArmorIQClient(api_key=api_key, user_id=user_id, agent_id=agent_id)
        plan = _build_plan(command, intent, market_data)

        captured = client.capture_plan(
            llm="gemini-2.5-flash",
            prompt=command,
            plan=plan,
            metadata={"app": "armor-guard", "environment": os.getenv("ENV", "local")},
        )
        token_response = client.get_intent_token(captured, validity_seconds=300)

        plan_hash = getattr(token_response, "plan_hash", "")
        merkle_root = getattr(token_response, "merkle_root", "")
        expires_at = getattr(token_response, "expires_at", None)

        # Compatibility fallback if SDK returns plain dict-like responses.
        if not plan_hash and hasattr(token_response, "get"):
            plan_hash = token_response.get("plan_hash", "")
            merkle_root = token_response.get("merkle_root", "")
            expires_at = token_response.get("expires_at")

        return {
            "enabled": True,
            "success": True,
            "plan_hash": plan_hash,
            "merkle_root": merkle_root,
            "expires_at": expires_at,
        }
    except Exception as exc:
        return {
            "enabled": True,
            "success": False,
            "reason": str(exc),
        }
