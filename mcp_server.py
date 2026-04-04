"""
Minimal MCP server for ArmorGuard registration/testing.
Provides a single tool: execute_trade.
"""

import os
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SERVER_NAME = os.getenv("MCP_SERVER_NAME", "armorguard-trading-mcp")
MCP_API_KEY = os.getenv("MCP_SERVER_API_KEY", "")


def _is_authorized(req) -> bool:
    if not MCP_API_KEY:
        return True

    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and auth.split(" ", 1)[1] == MCP_API_KEY:
        return True

    if req.headers.get("x-api-key", "") == MCP_API_KEY:
        return True

    return False


@app.get("/health")
def health():
    return jsonify({"ok": True, "server": SERVER_NAME})


@app.post("/mcp")
def mcp():
    if not _is_authorized(request):
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    method = payload.get("method", "")
    req_id = payload.get("id")

    def ok(result):
        return jsonify({"jsonrpc": "2.0", "id": req_id, "result": result})

    def err(code: int, message: str):
        return jsonify({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})

    if method == "initialize":
        return ok(
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": SERVER_NAME, "version": "0.1.0"},
                "capabilities": {"tools": {"listChanged": False}},
            }
        )

    if method == "tools/list":
        return ok(
            {
                "tools": [
                    {
                        "name": "execute_trade",
                        "description": "Execute/simulate a trade for ArmorGuard",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string", "enum": ["BUY", "SELL"]},
                                "ticker": {"type": "string"},
                                "qty": {"type": "integer", "minimum": 1},
                            },
                            "required": ["action", "ticker", "qty"],
                        },
                    }
                ]
            }
        )

    if method == "tools/call":
        params = payload.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {})

        if name != "execute_trade":
            return err(-32601, f"Unknown tool: {name}")

        action = str(arguments.get("action", "")).upper()
        ticker = str(arguments.get("ticker", "")).upper()
        qty = int(arguments.get("qty", 1))

        if action not in {"BUY", "SELL"}:
            return err(-32602, "action must be BUY or SELL")
        if not ticker:
            return err(-32602, "ticker is required")
        if qty < 1:
            return err(-32602, "qty must be >= 1")

        trade_id = f"mcp-{int(datetime.now(timezone.utc).timestamp())}"
        result = {
            "trade_id": trade_id,
            "status": "SIMULATED",
            "action": action,
            "ticker": ticker,
            "qty": qty,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return ok(
            {
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Trade simulated: {action} {qty} {ticker}; "
                            f"trade_id={trade_id}"
                        ),
                    }
                ],
                "structuredContent": result,
            }
        )

    return err(-32601, f"Unknown method: {method}")


if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
