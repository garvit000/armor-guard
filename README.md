# 🛡️ ArmorGuard AI (Finalist Edition)

> **Secure autonomous paper trading platform.**
> Built for the **ArmorIQ × OpenClaw** financial security hackathon track.

---

## 🎯 What It Does

ArmorGuard AI is an advanced prototype demonstrating deterministic AI orchestration in finance. It utilizes a **Multi-Agent Workflow** to intercept natural language execution intents, assess market viability, definitively restrict dangerous behavior, and execute paper trades.

It separates **market intelligence**, **policy enforcement**, and **trade execution** into auditable agent layers.

---

## 🏗️ Multi-Agent Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Flask UI   │ ──▶ │ Analyst Agent│ ──▶ │  Risk Agent  │ ──▶ │ Trader Agent │
│(4-Pane Dash)│     │(Market Intel)│     │ (ArmorIQ)    │     │ (Alpaca/DB)  │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

1. **Analyst Agent (`agents/analyst.py`)**: Checks real or mocked market bounds, calculating SMA 20, SMA 50, and RSI constraints to provide baseline recommendation scores.
2. **Risk Agent (`agents/risk.py`)**: The policy core. Computes a continuous automated **Risk Score**. Bounds trades by Ticker Whitelist, Daily Volume Notional Limits, Max Quantities, and Market Hours.
3. **Trader Agent (`agents/trader.py`)**: Alpaca mock execution layer maintaining an SQLite Database (`core/db.py`) of persistent portfolios.
4. **Orchestrator (`orchestrator.py`)**: Oversees input intent parsing and conditional logic blocks (e.g. `if RSI < 30`).

---

## 🚀 Setup & Execution

### Prerequisites
- Python 3.10+
- pip

### Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the SQLite Execution Database
python core/db.py

# 3. Run the App
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Quick Test Scenarios

Use the left-pane Terminal Chat or preset buttons:

| Command | Expected Result | Why? |
|---|---|---|
| `buy 1 NVDA` | 🟢 **ALLOWED** | Valid asset, volume within risk limits. |
| `buy 10 TSLA` | 🔴 **BLOCKED** | Fails Ticker Whitelist AND Max Quantity limit. Risk Score hits 100. |
| `buy 1 AAPL outside hours` | 🔴 **BLOCKED** | Manual trigger to force a failed market-open check. |
| `buy 1 AAPL if RSI < 30` | 🟢 **ALLOWED** | Evaluates Analyst Agent metrics before sending intent to the Risk Agent. |

---

## 📸 Premium 4-Pane UI

The frontend (`templates/index.html` + `static/style.css`) is structured as a premium fintech trading client.
- **Left**: Terminal input supporting autonomous conditional trigger logic.
- **Center**: Lightweight Candlestick Charts & live intelligence cards.
- **Right**: ArmorIQ console providing live evaluation metrics and a segmented Risk Meter.
- **Bottom**: Persistent trade execution and evaluation database access.

---

## 📄 License
MIT — built for the ArmorIQ × OpenClaw Hackathon Finals.
