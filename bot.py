import discord
import os
import pytz
import openai
from datetime import datetime
from chart_engine import generate_all_charts, generate_weekly_charts
from macro_data import get_macro_events_for_today, get_earnings_for_today, get_sentiment_summary, get_past_week_events

# Setup
TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_NAME = "macro-dashboard"

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

client = discord.Client(intents=intents)

# === Positioning GPT logic ===
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

# === Daily macro post ===
def generate_daily_macro_message():
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    today = now.strftime("%A, %B %d")
