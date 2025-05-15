import discord
import os
import asyncio
import datetime

# Print startup confirmation
print("🚀 Starting EE Macro Bot...")

# Load bot token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading text and emoji
client = discord.Client(intents=intents)

# ✅ Event: on_ready
@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

# ✅ Event: on_message (for !test)
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!test":
        await message.channel.send("📈 Macro Bot is online and working!")

# ✅ Task: daily scheduled post at 7 AM EST
async def daily_macro_post():
    await client.wait_until_ready()
    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = client.get_channel(channel_id)

    while not client.is_closed():
        now = datetime.datetime.now()
        target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        print(f"🕒 Waiting {wait_time / 60:.1f} minutes until next macro post...")

        await asyncio.sleep(wait_time)

        if channel:
            await channel.send("📊 Good morning. Here's your daily macro update! (Charts coming soon...)")
        else:
            print("❌ Could not find the macro-dashboard channel.")

        await asyncio.sleep(60)  # wait a minute before looping

# ✅ Start scheduled task
client.loop.create_task(daily_macro_post())

# ✅ Start bot
client.run(TOKEN)
