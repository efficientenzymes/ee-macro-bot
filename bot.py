import discord
import os
import asyncio
import datetime

print("🚀 Starting EE Macro Bot...")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

# ✅ Daily post function
async def daily_macro_post():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while not bot.is_closed():
        now = datetime.datetime.now()
        target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)

        if now > target_time:
            target_time += datetime.timedelta(days=1)

        wait_time = (target_time - now).total_seconds()
        print(f"🕒 Waiting {wait_time / 60:.1f} minutes until next macro post...")

        await asyncio.sleep(wait_time)

        try:
            if channel:
                await channel.send("📊 Good morning. Here's your daily macro update! (Charts coming soon...)")
                print("✅ Macro update sent.")
            else:
                print("❌ Could not find the macro-dashboard channel.")
        except Exception as e:
            print(f"🚨 Error sending macro post: {e}")

        await asyncio.sleep(60)

# ✅ Bot class
class MacroBot(discord.Client):
    async def setup_hook(self):
        print("🧠 setup_hook: scheduling daily macro post")
        self.loop.create_task(daily_macro_post())

# ✅ Bot instance
bot = MacroBot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "!test":
        await message.channel.send("📈 Macro Bot is online and working!")

bot.run(TOKEN)
