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
        prompt = (
            "You are a macro trader. Based on charts showing spreads like BTC/VIX, SPX/DXY, QQQ/IWM, "
            "summarize the big picture risk tone (risk-on/risk-off) in one sentence."
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
            chart_output, summary = generate_daily_macro_message()
            await message.channel.send(summary)

            if chart_output:
                await message.channel.send("📈 **Tracking asset class spreads to monitor risk flows**")
                for path, text in chart_output:
                    if os.path.isfile(path):
                        await message.channel.send(file=discord.File(path))
                        await message.channel.send(text)
                        await asyncio.sleep(1.5)

                # GPT chart interpretation
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
