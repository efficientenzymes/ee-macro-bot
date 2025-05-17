
import discord
import os
import pytz
import logging
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

# other imports...

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

    # ... existing daily/weekly logic here ...
