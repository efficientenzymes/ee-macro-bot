
import discord
import os
import asyncio
import datetime

print("🚀 Starting EE Macro Bot...")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# ✅ Daily 7 AM posting task
async def daily_macro_post():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        now = datetime.datetime.now()
        target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        print(f"🕒 Waiting {wait_time/60:.1f} minutes until next macro post...")

        await asyncio.sleep(wait_time)

        if channel:
            await channel.send("📊 Good morning. Here's your daily macro update! (Charts coming soon...)")
        else:
            print("❌ Could not find macro-dashboard channel")

        await asyncio.sleep(60)

# ✅ Modern startup hook
class MacroBot(discord.Client):
    async def setup_hook(self):
        print("🧠 Setup hook called – scheduling daily macro post")
        self.loop.create_task(daily_macro_post())

# ✅ Replace old client with MacroBot
client = MacroBot(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "!test":
        await message.channel.send("📈 Macro Bot is online and working!")

client.run(TOKEN)
