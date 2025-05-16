import discord
import os
import pytz
import openai
from datetime import datetime
from chart_engine import generate_all_charts, generate_weekly_charts
from macro_data import (
    get_macro_events_for_today,
    get_earnings_for_today,
    get_sentiment_summary,
    get_past_week_events,
)

# Setup
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

def generate_positioning_blurb(events, sentiment, is_weekly=False):
    prompt = f"""You're a seasoned macro trader writing a 1–2 sentence market prep summary. 
Today’s macro events: {', '.join(events[:5])}
Sentiment: VIX={sentiment['vix']} ({sentiment['vix_level']}), MOVE={sentiment['move']} ({sentiment['move_level']}), Put/Call={sentiment['put_call']} ({sentiment['put_call_level']})
Context: {'Weekly wrap' if is_weekly else 'Premarket plan'}

Tone: blunt, practical, non-bot, avoid generic advice.
Examples:
- “CPI sets the tone — any upside surprise could fuel a quick fade.”
- “Bonds tame, but risk assets look tired. Watch for rotation.”

Now generate one in that tone:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT error: {e}")
        return None

def generate_daily_macro_message():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    today = now.strftime("%A, %B %d")

    macro_section = get_macro_events_for_today()
    earnings_section = get_earnings_for_today()
    sentiment = get_sentiment_summary()
    chart_paths = generate_all_charts()

    summary_lines = []

    if macro_section:
        summary_lines.append("🗓️ Economic Events:")
        for event in macro_section[:5]:
            summary_lines.append(f"• {event}")
    else:
        summary_lines.append("🗓️ Economic Events: None scheduled")

    if earnings_section:
        summary_lines.append("\n💰 Earnings Highlights:")
        summary_lines.extend(f"• {line}" for line in earnings_section[:5])

    summary_lines.append("\n📊 Sentiment Snap:")
    summary_lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
    summary_lines.append(f"• Put/Call Ratio: {sentiment['put_call']} ({sentiment['put_call_level']})")
    summary_lines.append(f"• MOVE Index: {sentiment['move']} ({sentiment['move_level']})")

    gpt_blurb = generate_positioning_blurb(macro_section, sentiment)
    if gpt_blurb:
        summary_lines.append(f"\n🎯 {gpt_blurb}")

    summary_block = f"📅 **What to Watch Today – {today}**\n" + "\n".join(summary_lines)
    return chart_paths, summary_block

def generate_weekly_macro_message():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    week_ending = now.strftime("%A, %B %d")

    macro_section = get_past_week_events()
    sentiment = get_sentiment_summary()
    chart_paths = generate_weekly_charts()

    summary_lines = []

    summary_lines.append("🗓️ Key Events This Week:")
    if macro_section:
        summary_lines.extend(f"• {event}" for event in macro_section[:7])
    else:
        summary_lines.append("• No major events logged.")

    summary_lines.append("\n📊 Current Sentiment:")
    summary_lines.append(f"• VIX: {sentiment['vix']} ({sentiment['vix_level']})")
    summary_lines.append(f"• Put/Call Ratio: {sentiment['put_call']} ({sentiment['put_call_level']})")
    summary_lines.append(f"• MOVE Index: {sentiment['move']} ({sentiment['move_level']})")

    gpt_blurb = generate_positioning_blurb(macro_section, sentiment, is_weekly=True)
    if gpt_blurb:
        summary_lines.append(f"\n🧠 {gpt_blurb}")

    summary_block = f"📆 **Weekly Macro Recap – Week Ending {week_ending}**\n" + "\n".join(summary_lines)
    return chart_paths, summary_block

@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user} ({client.user.id})")

@client.event
async def on_message(message):
    print(f"[DEBUG] Got message: '{message.content}' from {message.author}")

    if message.author == client.user:
        return

    content = message.content.lower()

    if content == "!post":
        try:
            await message.channel.send("⏳ Generating daily macro...")
            chart_paths, summary_block = generate_daily_macro_message()
            await message.channel.send(summary_block)
            for path in chart_paths:
                with open(path, 'rb') as f:
                    await message.channel.send(file=discord.File(f))
            print("✅ Daily macro posted successfully.")
        except Exception as e:
            await message.channel.send(f"❌ Error in !post: {e}")
            print(f"[ERROR] Failed !post: {e}")

    elif content == "!weekly":
        try:
            await message.channel.send("⏳ Generating weekly macro...")
            chart_paths, summary_block = generate_weekly_macro_message()
            await message.channel.send(summary_block)
            for path in chart_paths:
                with open(path, 'rb') as f:
                    await message.channel.send(file=discord.File(f))
            print("✅ Weekly macro posted successfully.")
        except Exception as e:
            await message.channel.send(f"❌ Error in !weekly: {e}")
            print(f"[ERROR] Failed !weekly: {e}")

    elif content == "!status":
        await message.channel.send("✅ Macro bot is online and ready.")

    elif content == "!test":
        await message.channel.send("🧪 Test message received.")
        try:
            chart_paths, summary_block = generate_daily_macro_message()
            await message.channel.send(summary_block)
            for path in chart_paths:
                with open(path, 'rb') as f:
                    await message.channel.send(file=discord.File(f))
        except Exception as e:
            await message.channel.send(f"❌ Error in !test: {e}")
            print(f"[ERROR] Failed !test: {e}")

client.run(TOKEN)
