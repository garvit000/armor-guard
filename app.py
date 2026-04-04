"""
ArmorGuard AI — Flask Application
===================================
Main entry-point. Wires together Orchestrator logic and provides endpoints
for the new 4-pane UI.
"""

from flask import Flask, render_template, request, jsonify
from orchestrator import OpenClawGateway, get_history, get_market_summary
from core.db import init_db
from agents import analyst

app = Flask(__name__)

# Initialize DB on startup
init_db()

@app.route("/")
def index():
    """Render the dashboard."""
    return render_template("index.html")

@app.route("/market")
def market():
    """Return live market summary for allowed tickers."""
    tickers = ["NVDA", "AAPL", "MSFT", "TSLA"] # Added TSLA for demo purposes
    summary = get_market_summary(tickers)
    return jsonify(summary)

@app.route("/trade", methods=["POST"])
def trade():
    """Process intent."""
    data = request.get_json(force=True)
    user_input = data.get("command", "").strip()

    if not user_input:
        return jsonify({"error": "Empty command."}), 400

    response = OpenClawGateway.process_command(user_input)
    return jsonify(response)

@app.route("/history")
def history():
    """Return action history."""
    return jsonify(get_history())

@app.route("/api/chart/<ticker>")
def chart_data(ticker):
    """Return historical bars for frontend lightweight charts."""
    bars = analyst.get_historical_bars(ticker.upper(), days=30)
    return jsonify(bars)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
