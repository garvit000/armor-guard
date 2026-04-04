"""
OpenClaw Gateway & Orchestrator — ArmorGuard AI
================================================
Implements the ArmorClaw secure architecture.
Dashboard -> OpenClaw Gateway (Generates signed Intent-Token) 
-> ArmorIQ Plugin (Verifies Token & Policy) -> Trader Agent.
"""

import json
import hashlib
import hmac
import time
from datetime import datetime, timezone
from base64 import b64encode
from agents import analyst, trader
from agents.risk import ArmorIQPlugin  # Wrap risk.py into a plugin class
from openclaw_agent import parse_intent
from armoriq_bridge import submit_intent_plan
from core.db import SessionLocal, ActionHistory

SECRET_KEY = b"ArmorClaw_Hackathon_Secret_Key_2026"

class OpenClawGateway:
    
    @staticmethod
    def generate_intent_token(intent: dict) -> str:
        """Sign the intent block with HMAC SHA256 to create an Intent-Token."""
        # Simple JWT-like payload for the hackathon
        payload = json.dumps(intent, sort_keys=True)
        # Create signature
        signature = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).digest()
        # Encode
        token = f"{b64encode(payload.encode('utf-8')).decode('utf-8')}.{b64encode(signature).decode('utf-8')}"
        return token

    @staticmethod
    def process_command(command: str) -> dict:
        """Gateway ingestion of Natural Language."""
        audit_trail = []
        
        def add_audit(actor, event, status="INFO", data=""):
            audit_trail.append({
                "time": datetime.now(timezone.utc).isoformat(),
                "actor": actor,
                "event": event,
                "status": status,
                "data": data
            })

        add_audit("USER", f"Submitted command: '{command}'")
        
        # 1. NLP Parse to Intent
        intent = parse_intent(command)
        parser_mode = intent.get("parser", "unknown") if isinstance(intent, dict) else "unknown"
        add_audit(
            "OpenClaw Gateway",
            "Natural Language Intent Parsing",
            status="OK" if "error" not in intent else "ERROR",
            data=f"parser={parser_mode}",
        )
        
        ticker = intent.get("ticker", "UNKNOWN")
        market_data = {}
        if ticker != "UNKNOWN":
            market_data = analyst.analyze(ticker)
            add_audit("Analyst Agent", f"Fetched metrics for {ticker}: RSI {market_data.get('rsi')}", status="OK")

        # 1.5 Push intent plan to real ArmorIQ cloud (Intent Intelligence dashboard)
        armoriq_result = submit_intent_plan(command, intent, market_data)
        if armoriq_result.get("enabled") and armoriq_result.get("success"):
            plan_hash = armoriq_result.get("plan_hash", "")
            add_audit(
                "ArmorIQ Cloud",
                "Intent plan captured",
                status="OK",
                data=f"plan_hash={plan_hash[:16]}..." if plan_hash else "plan captured",
            )
        elif armoriq_result.get("enabled"):
            add_audit(
                "ArmorIQ Cloud",
                "Intent plan submission failed",
                status="ERROR",
                data=armoriq_result.get("reason", "unknown error"),
            )
        else:
            add_audit(
                "ArmorIQ Cloud",
                "Intent plan submission skipped",
                status="INFO",
                data=armoriq_result.get("reason", "not configured"),
            )

        # 2. Gate Conditionals (Autonomous Triggers)
        cmd_lower = command.lower()
        condition_met = True
        condition_msg = ""
        parts = command.split(" if ", 1) if " if " in cmd_lower else [command]
        
        if len(parts) > 1:
            condition_str = parts[1].strip()
            import re
            m = re.search(r'(rsi|sma20|sma50)\s*(<|>|<=|>=|==)\s*(\d+)', condition_str, re.IGNORECASE)
            if m and not market_data.get("error"):
                trigger_metric = m.group(1).lower()
                trigger_condition = m.group(2)
                trigger_value = float(m.group(3))
                metric_val = market_data.get(trigger_metric)
                
                if metric_val is not None:
                    if trigger_condition == "<" and not (metric_val < trigger_value): condition_met = False
                    elif trigger_condition == ">" and not (metric_val > trigger_value): condition_met = False
                    elif trigger_condition == "<=" and not (metric_val <= trigger_value): condition_met = False
                    elif trigger_condition == ">=" and not (metric_val >= trigger_value): condition_met = False
                    
                    if not condition_met:
                        condition_msg = f"Trigger deferred: {trigger_metric.upper()} ({metric_val}) is not {trigger_condition} {trigger_value}."

        if not condition_met:
            add_audit("OpenClaw Gateway", condition_msg, status="DEFERRED")
            return OpenClawGateway._finalize_request(
                command, intent, market_data, 
                {"allowed": False, "risk_score": 0, "reasons": [condition_msg]}, 
                None, audit_trail, "", armoriq_result
            )

        # 3. Generate Secure Intent Token
        if "error" in intent:
            token = ""
            policy_result = {"allowed": False, "risk_score": 100, "reasons": [intent["error"]]}
        else:
            token = OpenClawGateway.generate_intent_token(intent)
            add_audit("OpenClaw Crypto", "Intent-Token Generated & Signed", status="OK", data=token[-15:]+"...") # Show trailing chars as hash preview

            # 4. Intercept: ArmorIQ Plugin
            # We pass the TOKEN to the plugin, not the raw intent dict, enforcing secure architecture.
            force_hours_fail = "outside hours" in cmd_lower or "out of hours" in cmd_lower
            
            plugin = ArmorIQPlugin(SECRET_KEY)
            policy_result, plugin_audits = plugin.intercept_and_verify(token, market_data, force_hours_fail)
            audit_trail.extend(plugin_audits)

        # 5. Execution (if Plugin authorizes)
        exec_result = None
        if policy_result.get("allowed", False):
            exec_result = trader.execute(intent, market_data)
            add_audit("Trader Agent", f"Execution successful. Order ID: {exec_result['order_id']}", status="OK")
        else:
            if "error" not in intent:
                add_audit("Execution Layer", "Trade blocked by ArmorIQ Plugin", status="BLOCKED")

        return OpenClawGateway._finalize_request(
            command, intent, market_data, policy_result, exec_result, audit_trail, token, armoriq_result
        )

    @staticmethod
    def _finalize_request(command, intent, market_data, policy_result, exec_result, audit_trail, token, armoriq_result=None):
        session = SessionLocal()
        try:
            log_entry = ActionHistory(
                command=command,
                intent_token=token,
                ticker=intent.get("ticker", ""),
                action=intent.get("action", ""),
                qty=intent.get("qty", 0),
                status="ALLOWED" if policy_result.get("allowed") else "BLOCKED",
                reasons=json.dumps(policy_result.get("reasons", [])),
                audit_trail=json.dumps(audit_trail)
            )
            session.add(log_entry)
            session.commit()
        finally:
            session.close()

        return {
            "input": command,
            "intent": intent,
            "token": token,
            "market_data": market_data,
            "policy": policy_result,
            "execution": exec_result,
            "audit_trail": audit_trail,
            "armoriq": armoriq_result or {}
        }

def get_history():
    """Fetch recent action history."""
    session = SessionLocal()
    try:
        logs = session.query(ActionHistory).order_by(ActionHistory.timestamp.desc()).limit(50).all()
        return [
            {
                "id": l.id,
                "command": l.command,
                "token": l.intent_token,
                "ticker": l.ticker,
                "action": l.action,
                "qty": l.qty,
                "status": l.status,
                "reasons": json.loads(l.reasons) if l.reasons else [],
                "audit_trail": json.loads(l.audit_trail) if l.audit_trail else [],
                "timestamp": l.timestamp.isoformat()
            } for l in logs
        ]
    finally:
        session.close()

def get_market_summary(tickers: list) -> dict:
    summary = {}
    for t in tickers:
        summary[t] = analyst.analyze(t)
    return summary
