import discord
import os
import asyncio
import datetime

print("🚀 Starting EE Macro Bot...")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

# ✅ Bot Class With setup_hook and internal daily task
class MacroBot(discord.Client):
    async def setup_hook(self):
        print("🧠 setup_hook started")
        await asyncio.sleep(2)
        print("🔄 setup_hook scheduling daily task now")
        self.loop.create_task(self.daily_macro_post())

    async def daily_macro_post(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)
        
        while not self.is_closed():
            now = datetime.datetime.now()
            target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
            
            if now > target_time:
                target_time += datetime.timedelta(days=1)
            
            wait_time = (target_time - now).total_seconds()
            print(f"⏳ Waiting {wait_time / 60:.1f} minutes until next macro post...")
            
            await asyncio.sleep(wait_time)
            
            if channel:
                await channel.send("📊 Good morning. Here's your daily macro update! (Charts coming soon...)")
            else:
                print("❌ Could not find the macro-dashboard channel.")
            
            await asyncio.sleep(60)

# ✅ Instantiate Bot
bot = MacroBot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.lower() == "!test":
        await message.channel.send("📊 Macro Bot is online and working!")

bot.run(TOKEN)