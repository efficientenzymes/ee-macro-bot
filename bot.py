import discord
import os
import pytz
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

from sentiment_score import calculate_sentiment_score
from liquidity_tracker import get_liquidity_summary
from correlation_engine import get_correlation_summary
from narrative_heatmap import generate_narrative_heatmap
from macro_data import (
    get_macro_events_for_today,
    get_macro_events_for_tomorrow,
    get_earnings_for_today,
    get_earnings_for_tomorrow,
    get_sentiment_summary
)

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macro-bot")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = "macro-dashboard"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

def generate_daily_macro_message():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    today = now.strftime("%A, %B %d")

    macro_events = get_macro_events_for_today()
    earnings = get_earnings_for_today()
    sentiment = get_sentiment_summary()

    try:
        chart_output = generate_all_charts()
    except Exception as e:
        logger.error(f"[ERROR] Chart generation failed: {e}")
        chart_output = []

    lines = [f"📅 **What to Watch Today – {today}**"]

    if macro_events:
        lines.append("🗓️ Economic Events:")
        lines.extend(f"• {e}" for e in macro_events)
    else:
        lines.append("🗓️ Economic Events:\n• None")

    lines.append("\n💰 Earnings Highlights:")
    if earnings:
        lines.extend(f"• {e}" for e in earnings)
    else:
        lines.append("• None scheduled")

    lines.append("\n📊 Sentiment Snapshot:")
    lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
    lines.append(f"• MOVE: {sentiment['move']} ({sentiment['move_level']})")
    lines.append(f"• Put/Call: {sentiment['put_call']} ({sentiment['put_call_level']})")

    try:
        spread_metrics = extract_sentiment_metrics_from_chart_output(chart_output)
        score_summary = calculate_sentiment_score({
            "btc_vix_ratio": spread_metrics["btc_vix_ratio"],
            "vix_level": float(sentiment["vix"]),
            "put_call_ratio": float(sentiment["put_call"]),
            "hyg_lqd_trend": spread_metrics["hyg_lqd_trend"],
            "spx_dxy_ratio": spread_metrics["spx_dxy_ratio"]
        })
        lines.append(f"\n🧠 Sentiment Summary:\n{score_summary}")
    except Exception as e:
        logger.error(f"[ERROR] Sentiment scoring failed: {e}")
        lines.append("\n🧠 Sentiment Summary: Unavailable")

    try:
        blurb = generate_positioning_blurb(macro_events, sentiment)
        lines.append(f"\n🎯 {blurb}")
    except Exception as e:
        logger.warning(f"[WARNING] Positioning blurb failed: {e}")
        lines.append("\n🎯 Positioning summary unavailable")

    return chart_output, "\n".join(lines), score_summary


client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info("✅ Logged in as %s", client.user)
    client.loop.create_task(schedule_checker())

async def schedule_checker():
    await client.wait_until_ready()

    # ✅ Safe channel lookup
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)

    if not channel:
        logger.error(f"❌ Channel '{CHANNEL_NAME}' not found or bot lacks access.")
        return

    logger.info(f"📡 Ready to post in: #{channel.name}")

    posted_today = {"daily": None, "weekly": None}

    while not client.is_closed():
        now = datetime.now(pytz.timezone("US/Eastern"))
        time_now = now.strftime("%H:%M")
        day_now = now.strftime("%A")

        # Example: Daily post logic
        if day_now in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if time_now == "07:00" and posted_today["daily"] != now.date():
                logger.info("📅 Running daily post")
                try:
                    # Assume generate_daily_macro_message() is defined elsewhere
                    chart_output, summary, _ = generate_daily_macro_message()
                    await channel.send(summary)

                    for path, text in chart_output:
                        if os.path.isfile(path):
                            await channel.send(file=discord.File(path))
                            await channel.send(text)
                            await asyncio.sleep(1.5)

                except Exception as e:
                    logger.error(f"[ERROR] Daily macro post failed: {e}")
                posted_today["daily"] = now.date()

        # Example: Weekly summary logic
        if day_now == "Saturday" and time_now == "10:00" and posted_today["weekly"] != now.date():
            logger.info("📆 Running weekly summary")
            try:
                # These functions/modules must exist in your code
                next_week = get_macro_events_for_tomorrow()
                earnings = get_earnings_for_tomorrow()
                summary = "🧭 Weekly Summary Coming Soon..."  # Stub

                await channel.send(summary)
                await channel.send("\n".join(next_week))
                await channel.send("\n".join(earnings))

                liquidity = get_liquidity_summary()
                await channel.send(liquidity)

                correlations = get_correlation_summary()
                await channel.send("\n".join(correlations))

                narrative = generate_narrative_heatmap(
                    chart_summaries=["BTC/VIX uptrend", "SPX/DXY weakening"],
                    sentiment_summary="+2 Neutral-Bullish",
                    liquidity_summary=liquidity,
                    correlation_lines=correlations
                )
                await channel.send(narrative)

            except Exception as e:
                logger.error(f"[ERROR] Weekly post failed: {e}")
            posted_today["weekly"] = now.date()

        await asyncio.sleep(30)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!post":
        await message.channel.send("⏳ Generating macro update...")
        try:
            chart_output, summary, _ = generate_daily_macro_message()
            await message.channel.send(summary)
            for path, text in chart_output:
                if os.path.isfile(path):
                    await message.channel.send(file=discord.File(path))
                    await message.channel.send(text)
                    await asyncio.sleep(1.5)
        except Exception as e:
            logger.error(f"[ERROR] !post failed: {e}")
            await message.channel.send(f"❌ Error: {e}")

    elif message.content.lower() == "!status":
        await message.channel.send("✅ Macro bot is online and ready.")

client.run(TOKEN)
