import discord
import os
import asyncio
import logging
from datetime import datetime
from macro_events_nextweek import get_macro_events_for_next_week

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("macro-bot")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_NAME = "macro-dashboard"

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f"✅ Logged in as {client.user}")
    channel = discord.utils.get(client.get_all_channels(), name=CHANNEL_NAME)
    if not channel:
        logger.error("❌ Channel not found.")
        return

    # Only run on Saturday at 10 AM EST
    now = datetime.now()
    if now.strftime("%A") != "Saturday" or now.hour != 10:
        logger.info("⏭️ Not scheduled time — skipping.")
        await client.close()
        return

    # Pull next week's macro events
    next_week_events = get_macro_events_for_next_week()
    lines = ["🧭 **Weekly Macro Recap**", "🔭 **Key Things to Watch Next Week:**"]
    if next_week_events:
        lines.extend(f"• {e}" for e in next_week_events)
    else:
        lines.append("• No major events scheduled.")

    await channel.send("\n".join(lines))
    await asyncio.sleep(1)
    await client.close()

client.run(TOKEN)
