import discord
import os
import pytz
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

from weekly_data_collector import get_past_week_summary
from weekly_macro_recap import get_weekly_macro_highlights
from chart_reboot_curated import generate_all_charts
from macro_data import (
    get_macro_events_for_today,
    get_earnings_for_today,
    get_sentiment_summary,
    get_macro_events_for_tomorrow,
    get_earnings_for_tomorrow
)
from positioning_summary import generate_positioning_blurb
from macro_events_nextweek import get_macro_events_for_next_week
from weekly_gpt_summary import generate_weekly_summary_gpt
from sentiment_score import calculate_sentiment_score
from liquidity_tracker import get_liquidity_summary
from correlation_engine import get_correlation_summary
from narrative_heatmap import generate_narrative_heatmap

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macro-bot")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = "macro-dashboard"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)

def extract_sentiment_metrics_from_chart_output(chart_output):
    def parse_change(text, tag):
        try:
            idx = text.find(f"{tag}:")
            if idx == -1:
                return None
            start = idx + len(tag) + 1
            end = text.find("%", start)
            return float(text[start:end].strip())
        except:
            return None

    btc_vix, spx_dxy, hyg_lqd = None, None, "flat"
    for path, desc in chart_output:
        if "BTC / VIX" in desc:
            btc_vix = parse_change(desc, "1D")
        elif "SPX / DXY" in desc:
            spx_dxy = parse_change(desc, "1D")
        elif "HYG / LQD" in desc:
            change = parse_change(desc, "1W")
            if change is not None:
                if change > 0.5:
                    hyg_lqd = "up"
                elif change < -0.5:
                    hyg_lqd = "down"
    return {
        "btc_vix_ratio": btc_vix or 0.0,
        "spx_dxy_ratio": spx_dxy or 0.0,
        "hyg_lqd_trend": hyg_lqd
    }

def generate_daily_macro_message():
    logger.info("[DEBUG] generate_daily_macro_message running")
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    today = now.strftime("%A, %B %d")

    macro_events = get_macro_events_for_today()
    earnings = get_earnings_for_today()
    sentiment = get_sentiment_summary()

    try:
        chart_output = generate_all_charts()
        logger.info(f"[DEBUG] Generated {len(chart_output)} chart(s)")
    except Exception as e:
        logger.error(f"[ERROR] generate_all_charts() failed: {e}")
        chart_output = []

    lines = [f"📅 **What to Watch Today – {today}**"]

    if macro_events:
        lines.append("🗓️ Economic Events:")
        lines.extend(f"• {e}" for e in macro_events)
    else:
        lines.append("🗓️ Economic Events:\n• None")

    try:
        import openai
        client = openai.OpenAI()
        prompt = (
            "You're a macro strategist. Here's the economic calendar for today:\n" +
            "\n".join(macro_events) +
            "\n\nWrite a concise market-focused summary of what matters most."
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=60,
        )
        lines.append(f"\n🧠 {response.choices[0].message.content.strip()}")
    except Exception as e:
        logger.warning(f"[WARNING] GPT macro blurb failed: {e}")

    lines.append("\n💰 Earnings Highlights:")
    if earnings:
        lines.extend(f"• {e}" for e in earnings)
    else:
        lines.append("• No major earnings today")

    try:
        tickers = [e.split(":")[-1].strip() for e in earnings]
        prompt = (
            "Which of these earnings might move markets today and why?\n" +
            ", ".join(tickers)
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=60,
        )
        lines.append(f"\n🧠 {response.choices[0].message.content.strip()}")
    except Exception as e:
        logger.warning(f"[WARNING] GPT earnings blurb failed: {e}")

    lines.append("\n📊 Sentiment Snapshot:")
    lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
    lines.append(f"• MOVE Index: {sentiment['move']} ({sentiment['move_level']})")
    lines.append(f"• Put/Call Ratio: {sentiment['put_call']} ({sentiment['put_call_level']})")

    try:
        spread_metrics = extract_sentiment_metrics_from_chart_output(chart_output)
        score_summary = calculate_sentiment_score({
            "btc_vix_ratio": spread_metrics["btc_vix_ratio"],
            "vix_level": float(sentiment['vix']),
            "put_call_ratio": float(sentiment['put_call']),
            "hyg_lqd_trend": spread_metrics["hyg_lqd_trend"],
            "spx_dxy_ratio": spread_metrics["spx_dxy_ratio"]
        })
        lines.append(f"\n🧠 Sentiment Summary:\n{score_summary}")
    except Exception as e:
        lines.append("\n🧠 Sentiment Summary: Error generating score")
        logger.error(f"[ERROR] Sentiment score failed: {e}")

    try:
        blurb = generate_positioning_blurb(macro_events, sentiment)
        lines.append(f"\n🎯 {blurb}")
    except Exception as e:
        lines.append("\n🎯 Positioning Summary: Error")
        logger.error(f"[ERROR] Positioning blurb failed: {e}")

    try:
        tomorrow = (now + timedelta(days=1)).strftime("%A, %B %d")
        macro_tmr = get_macro_events_for_tomorrow()
        earnings_tmr = get_earnings_for_tomorrow()
        if macro_tmr or earnings_tmr:
            preview_prompt = "Write a sharp preview of tomorrow's key market-moving events."
            combined = "\n".join(macro_tmr + earnings_tmr)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": preview_prompt + "\n" + combined}],
                temperature=0.5,
                max_tokens=100,
            )
            lines.append(f"\n🧭 What to Watch Tomorrow – {tomorrow}")
            lines.append(response.choices[0].message.content.strip())
    except Exception as e:
        logger.warning(f"[WARNING] Tomorrow preview failed: {e}")

    return chart_output, "\n".join(lines), score_summary  # score_summary for use later

async def generate_chart_summary_gpt():
    try:
        import openai
        client = openai.OpenAI()
        prompt = (
            "You're a macro strategist. Based on chart spread summaries like BTC/VIX and SPX/DXY, "
            "write a one-sentence summary of current risk appetite."
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=60,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"[WARNING] Chart GPT summary failed: {e}")
        return None

@client.event
async def on_ready():
    logger.info("✅ Logged in as %s", client.user)
    client.loop.create_task(schedule_checker())

async def schedule_checker():
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)

    if not channel:
        logger.error("❌ Channel 'macro-dashboard' not found.")
        return

    posted_today = {"daily": None, "weekly": None}

    while not client.is_closed():
        now = datetime.now(pytz.timezone("US/Eastern"))
        time_now = now.strftime("%H:%M")
        day_now = now.strftime("%A")

        if day_now in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if time_now == "07:00" and posted_today["daily"] != now.date():
                try:
                    chart_output, summary, _ = generate_daily_macro_message()
                    await channel.send(summary)

                    if chart_output:
                        await channel.send("📈 **Tracking asset class spreads**")
                        for path, text in chart_output:
                            if os.path.isfile(path):
                                await channel.send(file=discord.File(path))
                                await channel.send(text)
                                await asyncio.sleep(1.5)

                        gpt_summary = await generate_chart_summary_gpt()
                        if gpt_summary:
                            await channel.send(f"🧠 {gpt_summary}")
                except Exception as e:
                    logger.error(f"[ERROR] Daily post failed: {e}")
                posted_today["daily"] = now.date()

        if day_now == "Saturday" and time_now == "10:00" and posted_today["weekly"] != now.date():
            try:
                next_week = get_macro_events_for_next_week()
                macro_highlights = get_weekly_macro_highlights()
                sentiment_and_earnings = get_past_week_summary()
                past_week = macro_highlights + sentiment_and_earnings

                lines = ["🧭 **Weekly Macro Recap**", "🔭 **Next Week:**"]
                lines.extend(f"• {e}" for e in next_week or ["No scheduled events."])

                recap = generate_weekly_summary_gpt(past_week, next_week)
                if recap:
                    lines.append(f"\n🧠 {recap}")

                await channel.send("\n".join(lines))

                # Liquidity Tracker
                liquidity_summary = get_liquidity_summary()
                await channel.send(liquidity_summary)

                # Correlation Matrix
                correlation_lines = get_correlation_summary()
                await channel.send("\n".join(correlation_lines))

                # Narrative Heatmap
                chart_output, _, sentiment_summary = generate_daily_macro_message()
                narrative = generate_narrative_heatmap(
                    chart_summaries=[text for _, text in chart_output],
                    sentiment_summary=sentiment_summary,
                    liquidity_summary=liquidity_summary,
                    correlation_lines=correlation_lines
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
            gpt_summary = await generate_chart_summary_gpt()
            if gpt_summary:
                await message.channel.send(f"🧠 {gpt_summary}")
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")
            logger.error(f"[ERROR] !post failed: {e}")

    elif message.content.lower() == "!status":
        await message.channel.send("✅ Macro bot is online and ready.")
