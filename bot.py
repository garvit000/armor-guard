"""
Discord Bot UI Layer — ArmorGuard AI
=====================================
Connects Discord to the OpenClaw Gateway and provides Portfolio/Charting.
"""

import os
import io
import json
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

import matplotlib
matplotlib.use('Agg') # Server-safe headless rendering
import matplotlib.pyplot as plt

# Import the existing secure backend
from orchestrator import OpenClawGateway
from agents import analyst

load_dotenv()

# Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ArmorGuard Discord UI Active. Logged in as {bot.user}")

@bot.command(name="trade")
async def trade_command(ctx, *, command_text: str):
    """
    Handle natural language commands.
    Usage: !trade buy 1 NVDA
    """
    processing_msg = await ctx.send("🛡️ **OpenClaw Gateway**: Intercepting intent. Cryptographic verification pending...")
    response = OpenClawGateway.process_command(command_text)
    
    policy = response.get("policy", {})
    allowed = policy.get("allowed", False)
    embed_color = discord.Color.green() if allowed else discord.Color.red()
    status_text = "ALLOWED" if allowed else "BLOCKED"
    
    embed = discord.Embed(
        title=f"ArmorClaw Verification: {status_text}",
        description=f"**Command parsed:** `{command_text}`",
        color=embed_color
    )
    
    audits = response.get("audit_trail", [])
    crypto_pass = any(a.get("event") == "Cryptographic Verification" and a.get("status") == "OK" for a in audits)
    
    if crypto_pass:
        embed.add_field(name="Intent Token Status", value="✅ VERIFIED BY ARMORIQ PLUGIN", inline=False)
        embed.add_field(name="Token Hash", value=f"`{response.get('token', 'N/A')}`", inline=False)
    else:
        embed.add_field(name="Intent Token Status", value="❌ VERIFICATION FAILED", inline=False)

    reasons = "\n".join(f"• {r}" for r in policy.get("reasons", ["No specific reason."]))
    embed.add_field(name="Policy Engine Output", value=reasons, inline=False)
    
    intent_json = json.dumps(response.get("intent", {}), indent=2)
    embed.add_field(name="Parsed Intent Payload", value=f"```json\n{intent_json}\n```", inline=False)
    
    if allowed and response.get("execution"):
        exec_info = response.get("execution")
        embed.add_field(name="Trader Agent Execution", value=f"Order ID: `{exec_info.get('order_id')}`\nNotional: `${exec_info.get('notional')}`", inline=False)
    
    embed.set_footer(text="ArmorGuard AI Audit Core", icon_url="https://ui-avatars.com/api/?name=AG&background=eab308&color=09090b")
    await processing_msg.edit(content=None, embed=embed)

@bot.command(name="portfolio")
async def portfolio_command(ctx):
    """View Alpaca Paper Portfolio."""
    key_id = os.getenv("ALPACA_API_KEY", "")
    secret_key = os.getenv("ALPACA_API_SECRET", "")
    
    if not key_id or key_id == "your_alpaca_api_key_here":
        await ctx.send("❌ **Error**: Alpaca API keys are missing from `.env`.")
        return
        
    headers = {"APCA-API-KEY-ID": key_id, "APCA-API-SECRET-KEY": secret_key, "accept": "application/json"}
    
    try:
        # Fetch Account
        acc_res = requests.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
        if acc_res.status_code != 200:
            await ctx.send(f"❌ **API Error**: {acc_res.text}")
            return
        acc_data = acc_res.json()
        
        # Fetch Positions
        pos_res = requests.get("https://paper-api.alpaca.markets/v2/positions", headers=headers)
        pos_data = pos_res.json() if pos_res.status_code == 200 else []
        
        embed = discord.Embed(title="📊 Alpaca Paper Portfolio", color=discord.Color.blue())
        embed.add_field(name="Portfolio Equity", value=f"${float(acc_data['equity']):,.2f}", inline=True)
        embed.add_field(name="Buying Power", value=f"${float(acc_data['buying_power']):,.2f}", inline=True)
        embed.add_field(name="Cash Balance", value=f"${float(acc_data['cash']):,.2f}", inline=True)
        
        holdings = []
        for p in pos_data:
            profit = float(p['unrealized_plpc']) * 100
            sign = "+" if profit >= 0 else ""
            holdings.append(f"**{p['symbol']}**: {p['qty']} shares | ${float(p['market_value']):,.2f} ({sign}{profit:.2f}%)")
            
        if holdings:
            embed.add_field(name="Current Holdings", value="\n".join(holdings), inline=False)
        else:
            embed.add_field(name="Current Holdings", value="*No active positions.*", inline=False)
            
        embed.set_footer(text="ArmorGuard Operations", icon_url="https://ui-avatars.com/api/?name=AG&background=3B82F6&color=FFF")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ **Error fetching portfolio**: {str(e)}")

@bot.command(name="graph")
async def graph_command(ctx, ticker: str):
    """Generate a 30-day performance graph for a ticker."""
    msg = await ctx.send(f"📈 Fetching live structural graph for `{ticker.upper()}`...")
    
    bars = analyst.get_historical_bars(ticker.upper(), days=30)
    if not bars:
        await msg.edit(content=f"❌ **Error**: Failed to retrieve market data for `{ticker.upper()}`.")
        return
        
    try:
        # Style the plot to match our Dark Theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(8, 4))
        
        dates = [b['time'] for b in bars]
        prices = [b['value'] for b in bars]
        
        ax.plot(dates, prices, color='#3B82F6', linewidth=2, marker='o', markersize=4)
        ax.set_title(f"{ticker.upper()} - 30 Day Performance", color='white', pad=20)
        ax.set_ylabel("Price (USD)", color='#A1A1AA')
        ax.grid(color='#27272A', linestyle='--', linewidth=0.5)
        
        # Clean up x-axis labels to avoid crowding
        ax.set_xticks([dates[0], dates[len(dates)//2], dates[-1]])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#27272A')
        ax.spines['left'].set_color('#27272A')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#18181B')
        buf.seek(0)
        plt.close(fig)

        file = discord.File(fp=buf, filename=f'{ticker.upper()}_chart.png')
        await msg.delete()
        await ctx.send(file=file)
    except Exception as e:
        await msg.edit(content=f"❌ **Rendering Error**: {str(e)}")

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token and token != "your_discord_bot_token_here":
        bot.run(token)
    else:
        print("\n[!] WARNING: DISCORD_BOT_TOKEN is not set in .env")
