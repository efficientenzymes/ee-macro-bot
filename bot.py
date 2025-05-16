import discord
import os
import pytz
from datetime import datetime
from chart_engine import generate_all_charts
from macro_data import (
    get_macro_events_for_today,
    get_earnings_for_today,
    get_sentiment_summary
)
from positioning_summary import generate_positioning_blurb

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

def generate_daily_macro_message():
    print("[DEBUG] generate_daily_macro_message running")
    
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    today = now.strftime("%A, %B %d")

    macro_events = get_macro_events_for_today()
    earnings = get_earnings_for_today()
    sentiment = get_sentiment_summary()
    chart_paths = generate_all_charts()

    lines = []
    lines.append(f"📅 **What to Watch Today – {today}**")

    if macro_events:
        lines.append("🗓️ Economic Events:")
        lines.extend(f"• {e}" for e in macro_events)

    if earnings:
        lines.append("\n💰 Earnings Highlights:")
        lines.extend(f"• {e}" for e in earnings)

    lines.append("\n📊 Sentiment Snapshot:")
    lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
    lines.append(f"• MOVE Index: {sentiment['move']} ({sentiment['move_level']})")
    lines.append(f"• Put/Call Ratio: {sentiment['put_call']} ({sentiment['put_call_level']})")

    # ✅ Ensure GPT is called
    blurb = generate_positioning_blurb(macro_events, sentiment)
    lines.append(f"\n🎯 {blurb}")

    return chart_paths, "\n".join(lines)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.lower()

    if content == "!post":
        await message.channel.send("⏳ Generating macro update...")
        try:
            chart_paths, summary = generate_daily_macro_message()
            await message.channel.send(summary)
            for path in chart_paths:
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        await message.channel.send(file=discord.File(f))
            print("✅ Posted macro update.")
        except Exception as e:
            print(f"❌ Error in !post: {e}")
            await message.channel.send(f"❌ Error: {e}")

    elif content == "!status":
        await message.channel.send("✅ Macro bot is online and running.")

client.run(TOKEN)
