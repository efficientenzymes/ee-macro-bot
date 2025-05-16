import discord
import os
import pytz
import logging
import asyncio
from datetime import datetime
from chart_reboot_curated import generate_all_charts
from macro_data import (
    get_macro_events_for_today,
    get_earnings_for_today,
    get_sentiment_summary
)
from positioning_summary import generate_positioning_blurb
from macro_events_nextweek import get_macro_events_for_next_week
from weekly_gpt_summary import generate_weekly_summary_gpt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macro-bot")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = "macro-dashboard"

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

        try:
            chart_output = generate_all_charts()
            logger.info(f"[DEBUG] Generated {len(chart_output)} chart(s)")
        except Exception as e:
            logger.error(f"[ERROR] generate_all_charts() failed: {e}")
            chart_output = []

        lines = []
        lines.append(f"📅 **What to Watch Today – {today}**")

        if macro_events:
            lines.append("🗓️ Economic Events:")
            lines.extend(f"• {e}" for e in macro_events)
        else:
            lines.append("🗓️ Economic Events:\n• No major events found.")

        # GPT macro blurb
        try:
            if macro_events:
                import openai
                client = openai.OpenAI()
                prompt = (
                    "You're a macro strategist. Here is a list of today's economic events:\n" +
                    "\n".join(macro_events) +
                    "\n\nWrite 1 short sentence about what matters most for markets today."
                )
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=50,
                )
                macro_blurb = response.choices[0].message.content.strip()
                lines.append(f"\n🧠 {macro_blurb}")
        except Exception as e:
            logger.warning(f"[WARNING] GPT macro blurb failed: {e}")

        lines.append("\n💰 Earnings Highlights:")
        if earnings:
            lines.extend(f"• {e}" for e in earnings)
        else:
            lines.append("• No significant earnings today")

        # GPT earnings blurb
        try:
            if earnings:
                tickers = [e.split(":")[-1].strip() for e in earnings]
                prompt = (
                    f"You're a market analyst. Which of these companies might move the market today and why?\n" +
                    ", ".join(tickers) +
                    "\nRespond with one short sentence. Be sharp."
                )
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4,
                    max_tokens=50,
                )
                earnings_blurb = response.choices[0].message.content.strip()
                lines.append(f"\n🧠 {earnings_blurb}")
        except Exception as e:
            logger.warning(f"[WARNING] GPT earnings blurb failed: {e}")

        lines.append("\n📊 Sentiment Snapshot:")
        lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
        lines.append(f"• MOVE Index: {sentiment['move']} ({sentiment['move_level']})")
        lines.append(f"• Put/Call Ratio: {sentiment['put_call']} ({sentiment['put_call_level']})")

        logger.info("[DEBUG] About to call generate_positioning_blurb()")

        blurb = None
        try:
            blurb = generate_positioning_blurb(macro_events, sentiment)
            logger.info(f"[DEBUG] Received blurb: {blurb}")
        except Exception as e:
            logger.error(f"[ERROR] generate_positioning_blurb() raised exception: {e}")
            blurb = "Positioning failed — check logs"

        lines.append(f"\n🎯 {blurb}")
        return chart_output, "\n".join(lines)

    except Exception as e:
        logger.error(f"[ERROR] Exception in generate_daily_macro_message: {e}")
        raise

async def generate_chart_summary_gpt():
    try:
        import openai
        client = openai.OpenAI()
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            logger.warning("[WARNING] OPENAI_API_KEY not set.")
            return None

        prompt = (
            "You're a macro trader. Based on chart spreads like BTC/VIX, SPX/DXY, QQQ/IWM, "
            "summarize the market tone in one sharp sentence. Focus on risk-on vs risk-off."
        )

        logger.info("[DEBUG] Calling GPT for chart summary...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"[WARNING] Chart GPT summary failed: {e}")
        return None

async def schedule_checker():
    await client.wait_until_ready()
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)

    if not channel:
        logger.error("❌ Channel 'macro-dashboard' not found.")
        return

    posted_today = {"daily": None, "weekly": None}

    while not client.is_closed():
        now = datetime.now(pytz.timezone("US/Eastern"))
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")

        # Daily macro post at 7:00 AM EST
        if current_day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if current_time == "07:00" and posted_today["daily"] != now.date():
                logger.info("📅 Running scheduled daily macro post")
                try:
                    chart_output, summary = generate_daily_macro_message()
                    await channel.send(summary)

                    if chart_output:
                        await channel.send("📈 **Tracking asset class spreads to monitor risk flows**")
                        for path, text in chart_output:
                            if os.path.isfile(path):
                                await channel.send(file=discord.File(path))
                                await channel.send(text)
                                await asyncio.sleep(1.5)

                        chart_blurb = await generate_chart_summary_gpt()
                        if chart_blurb:
                            await channel.send(f"🧠 {chart_blurb}")
                except Exception as e:
                    logger.error(f"[ERROR] Scheduled daily macro post failed: {e}")

                posted_today["daily"] = now.date()

        # Weekly summary at 10:00 AM EST on Saturday
        if current_day == "Saturday":
            if current_time == "10:00" and posted_today["weekly"] != now.date():
                logger.info("📆 Running scheduled Saturday summary")
                try:
                    next_week_events = get_macro_events_for_next_week()
                    past_week_events = ["CPI print", "SPX breakout", "Put/Call ratio shifted"]  # manually listed or extend later

                    lines = ["🧭 **Weekly Macro Recap**", "🔭 **Key Things to Watch Next Week:**"]
                    if next_week_events:
                        lines.extend(f"• {e}" for e in next_week_events)
                    else:
                        lines.append("• No major events scheduled.")

                    recap = generate_weekly_summary_gpt(past_week_events, next_week_events)
                    if recap:
                        lines.append(f"\n🧠 {recap}")

                    await channel.send("\n".join(lines))

                except Exception as e:
                    logger.error(f"[ERROR] Scheduled weekly summary failed: {e}")

                posted_today["weekly"] = now.date()

        await asyncio.sleep(30)

@client.event
async def on_ready():
    logger.info("✅ Logged in as %s", client.user)
    client.loop.create_task(schedule_checker())

@client.event
async def on_message(message):
    logger.info("[DEBUG] Received message: %s", message.content)

    if message.author == client.user:
        return

    content = message.content.lower()

    if content == "!post":
        await message.channel.send("⏳ Generating macro update...")
        try:
            chart_output, summary = generate_daily_macro_message()
            await message.channel.send(summary)

            if chart_output:
                await message.channel.send("📈 **Tracking asset class spreads to monitor risk flows**")
                for path, text in chart_output:
                    if os.path.isfile(path):
                        await message.channel.send(file=discord.File(path))
                        await message.channel.send(text)
                        await asyncio.sleep(1.5)

                chart_blurb = await generate_chart_summary_gpt()
                if chart_blurb:
                    await message.channel.send(f"🧠 {chart_blurb}")

            logger.info("✅ Posted macro update.")

        except Exception as e:
            logger.error("❌ Error in !post: %s", e)
            await message.channel.send(f"❌ Error: {e}")

    elif content == "!status":
        await message.channel.send("✅ Macro bot is online and running.")

client.run(TOKEN)
