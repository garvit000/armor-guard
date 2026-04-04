"""
Discord Bot UI Layer — ArmorGuard AI
=====================================
Connects Discord to the OpenClaw Gateway.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json

# Import the existing secure backend
from orchestrator import OpenClawGateway

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
    # 1. Provide initial verification feedback
    processing_msg = await ctx.send("🛡️ **OpenClaw Gateway**: Intercepting intent. Cryptographic verification pending...")
    
    # 2. Re-use exact same orchestrator as the Dashboard
    response = OpenClawGateway.process_command(command_text)
    
    # 3. Format Discord output based on ArmorClaw architecture
    policy = response.get("policy", {})
    allowed = policy.get("allowed", False)
    
    embed_color = discord.Color.green() if allowed else discord.Color.red()
    status_text = "ALLOWED" if allowed else "BLOCKED"
    
    embed = discord.Embed(
        title=f"ArmorClaw Verification: {status_text}",
        description=f"**Command parsed:** `{command_text}`",
        color=embed_color
    )
    
    # Determine Plugin Verification Status from Audit Log
    audits = response.get("audit_trail", [])
    crypto_pass = any(a.get("event") == "Cryptographic Verification" and a.get("status") == "OK" for a in audits)
    
    if crypto_pass:
        embed.add_field(name="Intent Token Status", value="✅ VERIFIED BY ARMORIQ PLUGIN", inline=False)
        embed.add_field(name="Token Hash", value=f"`{response.get('token', 'N/A')}`", inline=False)
    else:
        embed.add_field(name="Intent Token Status", value="❌ VERIFICATION FAILED", inline=False)

    # Policy Reasons
    reasons = "\n".join(f"• {r}" for r in policy.get("reasons", ["No specific reason."]))
    embed.add_field(name="Policy Engine Output", value=reasons, inline=False)
    
    # Intent JSON (OpenClaw Output)
    intent_json = json.dumps(response.get("intent", {}), indent=2)
    embed.add_field(name="Parsed Intent Payload", value=f"```json\n{intent_json}\n```", inline=False)
    
    # Execution Info
    if allowed and response.get("execution"):
        exec_info = response.get("execution")
        embed.add_field(name="Trader Agent Execution", value=f"Order ID: `{exec_info.get('order_id')}`\nNotional: `${exec_info.get('notional')}`", inline=False)
    
    embed.set_footer(text="ArmorGuard AI Audit Core", icon_url="https://ui-avatars.com/api/?name=AG&background=eab308&color=09090b")
    
    await processing_msg.edit(content=None, embed=embed)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token and token != "your_discord_bot_token_here":
        bot.run(token)
    else:
        print("\n[!] WARNING: DISCORD_BOT_TOKEN is not set in .env")
        print("To run the Discord bot locally:")
        print("1. Go to Discord Developer Portal and create an app.")
        print("2. Copy the Bot Token.")
        print("3. Rename .env.example to .env and paste the token.")
        print("4. Re-run `python bot.py`\n")
