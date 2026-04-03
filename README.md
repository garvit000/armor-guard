# 🛡️ ArmorGuard AI

> **Intent-aware autonomous paper trading with policy-enforced security.**
> Built for the **ArmorIQ × OpenClaw** financial security hackathon track.

---

## 🎯 What It Does

ArmorGuard AI is a prototype that demonstrates how an autonomous AI agent can safely execute financial trades by separating **intent understanding**, **policy enforcement**, and **trade execution** into distinct, auditable layers.

A user types a natural-language trading command (e.g. `"buy 1 NVDA"`), and the system:

1. **Parses** the intent using an OpenClaw agent
2. **Evaluates** the parsed intent against a deterministic policy engine
3. **Executes** (or blocks) a simulated paper trade via Alpaca

Every decision is logged with full reasoning visibility.

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│   Flask UI  │ ──▶ │  OpenClaw Agent  │ ──▶ │ Policy Engine│ ──▶ │ Paper Trader │
│ (index.html)│     │ (intent parser)  │     │ (policy.py)  │     │ (trader.py)  │
└─────────────┘     └──────────────────┘     └──────────────┘     └──────────────┘
     User               Structured               ALLOW /              Simulated
   Natural             JSON Intent              BLOCK with            Alpaca Fill
   Language                                      Reasons
```

### File Map

| File | Purpose |
|---|---|
| `app.py` | Flask web server — wires all layers together |
| `openclaw_agent.py` | OpenClaw intent-parser agent — NL → JSON |
| `policy.py` | Deterministic policy engine — whitelist + quantity cap |
| `trader.py` | Simulated Alpaca paper-trade executor |
| `templates/index.html` | Dark trading dashboard UI |
| `static/style.css` | Premium CSS design system |

---

## 🤖 How OpenClaw Is Used

The `openclaw_agent.py` module acts as the **OpenClaw autonomous agent** layer:

- Takes arbitrary natural-language input from the user
- Converts it into a **structured JSON intent**:
  ```json
  { "ticker": "NVDA", "qty": 1, "action": "BUY" }
  ```
- Supports action verbs: `buy`, `purchase`, `acquire`, `sell`, `short`, `dump`, etc.
- Returns a clear error if the input cannot be parsed

In a production deployment, this module would call the OpenClaw SDK for more sophisticated NLP. For the hackathon prototype, we use deterministic regex-based parsing to ensure reliable offline demos.

---

## 🔒 Policy Engine Rules

The policy engine (`policy.py`) enforces three deterministic rules:

| # | Rule | Detail |
|---|---|---|
| 1 | **Ticker Whitelist** | Only `NVDA`, `AAPL`, `MSFT` are allowed |
| 2 | **Quantity Cap** | Maximum **2 shares** per trade |
| 3 | **Action Validation** | Only `BUY` and `SELL` are recognised |

If **any** rule is violated, the trade is **BLOCKED** and the exact violation reason(s) are returned to the UI. Trades only execute when **all** rules pass.

---

## 🚀 Setup

### Prerequisites

- Python 3.10+
- pip

### Install & Run

```bash
# 1. Clone the repo
git clone https://github.com/your-username/armor-guard.git
cd armor-guard

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🧪 Demo Test Cases

| # | Command | Expected | Reason |
|---|---|---|---|
| 1 | `buy 1 NVDA` | ✅ **ALLOWED** | Valid ticker, quantity ≤ 2 |
| 2 | `buy 100 NVDA` | 🚫 **BLOCKED** | Quantity 100 exceeds max of 2 |
| 3 | `buy 1 TSLA` | 🚫 **BLOCKED** | TSLA not in allowed ticker list |
| 4 | `sell 2 AAPL` | ✅ **ALLOWED** | Valid ticker, quantity ≤ 2, valid action |
| 5 | `buy 1 MSFT` | ✅ **ALLOWED** | Valid ticker, quantity ≤ 2 |

### Quick Demo Flow

1. Open the dashboard
2. Click the **quick-action chips** or type a command
3. Observe:
   - 🟢 **Green ALLOWED badge** + full execution log for valid trades
   - 🔴 **Red BLOCKED badge** + exact violation reasons for blocked trades
4. All trades appear in the **Activity Log** panel

---

## 📸 Screenshots

The dashboard features:

- **Pipeline architecture** diagram at the top
- **Natural language input** with quick-action chips
- **Syntax-highlighted JSON** showing the parsed OpenClaw intent
- **Policy evaluation** with pass/fail reasons
- **Execution log** grid for allowed trades
- **Activity log** tracking all commands

---

## 🛠️ Tech Stack

- **Backend:** Python / Flask
- **Agent Layer:** OpenClaw-style intent parser
- **Frontend:** Vanilla HTML/CSS/JS
- **Design:** Dark mode, glassmorphism, Inter + JetBrains Mono fonts

---

## 📄 License

MIT — built for the ArmorIQ × OpenClaw hackathon.
