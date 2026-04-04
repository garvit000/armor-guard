# 🛡️ ArmorGuard AI (ArmorClaw Edition)

> **Enterprise-grade secure autonomous trading platform.**
> Refactored to align with the official **ArmorIQ × OpenClaw** gateway architecture.

---

## 🎯 What It Does

ArmorGuard AI demonstrates a definitive secure architecture for autonomous financial AI. Instead of free-running agents, we enforce a strict **Gateway -> Plugin -> Execution** flow governed by cryptographic verification.

Every natural language trade command is converted into an **Intent-Token** which must pass cryptographic verification before any runtime policy evaluation or trade execution can occur.

---

## 🏗️ Secure Gateway Architecture

```
┌─────────────┐      ┌─────────────────────────┐      ┌─────────────────────────┐
│  Dashboard  │ ───▶ │    OpenClaw Gateway     │ ───▶ │     ArmorIQ Plugin      │
│  UI Console │      │ (NLP -> Signed Token)   │      │ (Verify -> Policy Gate) │
└─────────────┘      └─────────────────────────┘      └─────────────────────────┘
                                                                  │ (If Valid)
┌─────────────┐      ┌─────────────────────────┐                  ▼
│ SQLite Base │ ◀─── │      Trader Agent       │      ┌─────────────────────────┐
│ (Audit Log) │      │  (Simulated Alpaca)     │ ◀─── │   Execution Pipeline    │
└─────────────┘      └─────────────────────────┘      └─────────────────────────┘
```

1. **OpenClaw Gateway (`orchestrator.py`)**: Intercepts natural language, coordinates with the `Analyst Agent` for market context, construct the trade intent, and signs it via `HMAC SHA256` to generate the secure **Intent-Token**.
2. **ArmorIQ Plugin (`agents/risk.py`)**: Intercepts the generated Intent-Token. Synthetically verifies the cryptographic signature to ensure the payload wasn't tampered with mid-flight. If verified, the payload runs through strict policy limits (Market Hours, Whitelists, Exposure Ceilings).
3. **Trader Agent**: Executes the cleared action and writes a definitive execution receipt.
4. **Audit Timeline (`core/db.py`)**: Centralized, unalterable log tracking the micro-steps from parsing to execution for compliance visualization.

---

## 🚀 Setup & Execution

### Prerequisites
- Python 3.10+
- pip

### Install & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the SQLite Databases (Trade & Action AuditLogs)
python core/db.py

# 3. Run the Secure App
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🧪 Demo Scenarios

Use the left-pane Terminal Chat or preset buttons. **Check the bottom expandable data table for full Security Audit Timelines.**

| Command | Expected Result | Reason |
|---|---|---|
| `buy 1 NVDA` | 🟢 **ALLOWED** | Token verified. Valid asset, volume within risk limits. |
| `buy 100 AAPL` | 🔴 **BLOCKED** | Token verified, but payload fails Plugin Runtime Policy (Max Qty + Daily Threshold). |
| `buy 1 TSLA` | 🔴 **BLOCKED** | Token verified, but payload fails Plugin Runtime Whitelisting. |
| `buy 1 AAPL outside hours` | 🔴 **BLOCKED** | Token verified, but plugin detects mocked outside-hours condition. |

---

## 📸 Enterprise 4-Pane Dashboard

- **Left (Terminal)**: Command input supporting autonomous conditional trigger logic.
- **Center (Market Intel)**: Live updating intelligence cards & lightweight embedded charts.
- **Right (Plugin Security)**: Displays active **Intent-Token Verification hashes** and real-time ArmorIQ policy intercepts.
- **Bottom (Compliance & Audit)**: Interactive execution log with an expanding step-by-step audit trail for each interaction.

---

## 🤖 Discord Integration

ArmorGuard AI now supports a **Discord Bot UI** layer! It pipes directly into the exact same OpenClaw Gateway as the web dashboard, ensuring cryptographic token enforcement remains identical.

### Discord Setup
1. Duplicate `.env.example` to `.env`.
2. Retrieve a Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications).
3. Add your token to the `.env` file:
   ```env
   DISCORD_BOT_TOKEN="your-token-here"
   ```
4. Start the bot:
   ```bash
   python bot.py
   ```

**Usage in Discord:**
Use the `!trade` command followed by natural language.
- `!trade buy 1 NVDA`
- `!trade buy 100 TSLA`

The bot will reply with a Rich Embed containing the generated cryptographic token limit, the parsed JSON payload, the ArmorIQ policy decision, and the trader execution receipt.

---

## 📄 License
MIT — built for the ArmorIQ × OpenClaw Hackathon Finals.
