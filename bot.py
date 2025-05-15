import discord
import os
import asyncio
import datetime

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for reading emoji & slash
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):

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
            print("❌ Could not find the channel.")

        await asyncio.sleep(60)

    if message.author == client.user:
        return

    if message.content.lower() == "!test":
        await message.channel.send("Macro bot is online and ready.")

client.loop.create_task(daily_macro_post())

client.run(TOKEN)
