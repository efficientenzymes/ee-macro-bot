import discord
import os
import pytz
import logging
from datetime import datetime
from chart_engine import generate_all_charts
from macro_data import (
    get_macro_events_for_today,
    get_earnings_for_today,
    get_sentiment_summary
)
from positioning_summary import generate_positioning_blurb

# ✅ Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macro-bot")

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

def generate_daily_macro_message():
    logger.info("[DEBUG] generate_daily_macro_message running")

    try:
        eastern = pytz.timezone("US/Eastern")
        now = datetime.now(eastern)
        today = now.strftime("%A, %B %d")

        macro_events = get_macro_events_for_today()
        logger.info(f"[DEBUG] Retrieved macro events: {macro_events}")

        earnings = get_earnings_for_today()
        logger.info(f"[DEBUG] Retrieved earnings: {earnings}")

        sentiment = get_sentiment_summary()
        logger.info(f"[DEBUG] Retrieved sentiment: {sentiment}")

        chart_paths = generate_all_charts()
        logger.info(f"[DEBUG] Generated {len(chart_paths)} chart(s)")

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

        logger.info("[DEBUG] About to call generate_positioning_blurb()")

        blurb = None
        try:
            blurb = generate_positioning_blurb(macro_events, sentiment)
        except Exception as e:
            logger.error(f"[ERROR] generate_positioning_blurb() raised exception: {e}")

        logger.info(f"[DEBUG] Blurb returned: {blurb}")

        if not blurb:
            blurb = "Positioning failed — empty summary"

        lines.append(f"\n🎯 {blurb}")

        return chart_paths, "\n".join(lines)

    except Exception as e:
        logger.error(f"[ERROR] Exception in generate_daily_macro_message: {e}")
        raise

@client.event
async def on_ready():
    logger.info("✅ Logged in as %s", client.user)

@client.event
async def on_message(message):
    logger.info("[DEBUG] Received message: %s", message.content)

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
            logger.info("✅ Posted macro update.")
        except Exception as e:
            logger.error("❌ Error in !post: %s", e)
            await message.channel.send(f"❌ Error: {e}")

    elif content == "!status":
        await message.channel.send("✅ Macro bot is online and running.")

client.run(TOKEN)
