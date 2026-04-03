"""
ArmorGuard AI — Flask Application
===================================
Main entry-point.  Wires together the OpenClaw intent-parser,
the policy engine, and the paper-trade executor behind a single
``/trade`` API endpoint consumed by the dashboard UI.
"""

from flask import Flask, render_template, request, jsonify

from openclaw_agent import parse_intent
from policy import evaluate
from trader import execute

app = Flask(__name__)

# ── In-memory activity log (newest first) ─────────────────────────────
activity_log: list[dict] = []


@app.route("/")
def index():
    """Render the trading dashboard."""
    return render_template("index.html")


@app.route("/trade", methods=["POST"])
def trade():
    """
    End-to-end trade pipeline:
        user text → OpenClaw parse → policy check → (optional) execute
    """
    data = request.get_json(force=True)
    user_input = data.get("command", "").strip()

    if not user_input:
        return jsonify({"error": "Empty command."}), 400

    # Step 1 — Intent parsing (OpenClaw agent)
    intent = parse_intent(user_input)

    # Step 2 — Policy evaluation
    policy_result = evaluate(intent)

    # Step 3 — Conditional execution
    execution = None
    if policy_result.allowed:
        execution = execute(intent)

    # Build response payload
    response = {
        "input": user_input,
        "intent": intent,
        "policy": policy_result.to_dict(),
        "execution": execution,
    }

    # Persist to activity log
    activity_log.insert(0, response)

    return jsonify(response)


@app.route("/logs")
def logs():
    """Return the full activity log as JSON."""
    return jsonify(activity_log)


# ── Dev server ────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
