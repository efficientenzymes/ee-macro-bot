import discord
import os
import asyncio
import datetime
import sys
from chart_engine import generate_all_charts, generate_weekly_charts

print("🚀 Starting EE Macro Bot...")
print(f"🕒 Current time: {datetime.datetime.now()}")
sys.stdout.reconfigure(line_buffering=True)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1372316620093001891
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
TEST_INTERVAL_MINUTES = int(os.getenv("TEST_INTERVAL_MINUTES", "2"))

intents = discord.Intents.default()
intents.message_content = True

class MacroBot(discord.Client):
    async def setup_hook(self):
        print("🧠 setup_hook started")
        await asyncio.sleep(2)
        self.loop.create_task(self.daily_macro_post())
        self.loop.create_task(self.weekly_macro_post())

    async def daily_macro_post(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        while not self.is_closed():
            now = datetime.datetime.now()
            if TEST_MODE:
                wait_time = TEST_INTERVAL_MINUTES * 60
            else:
                target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
                if now > target_time:
                    target_time += datetime.timedelta(days=1)
                wait_time = (target_time - now).total_seconds()

            await asyncio.sleep(wait_time)

            if channel:
                try:
                    today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
                    await channel.send(f"📅 **EE Daily Macro Report – {today_str}**\nHere’s today’s snapshot of key macro ratios and breakouts.")
                    results, summary = generate_all_charts()
                    for file_path, caption in results:
                        await channel.send(file=discord.File(file_path))
                        await asyncio.sleep(1.1)
                        await channel.send(caption)
                        await asyncio.sleep(1.1)
                    if summary:
                        await channel.send(summary)
                except Exception as e:
                    print(f"❌ Error sending daily report: {e}")

            await asyncio.sleep(5)

    async def weekly_macro_post(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        while not self.is_closed():
            now = datetime.datetime.now()
            target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
            while now.weekday() != 5 or now > target_time:  # Saturday
                await asyncio.sleep(3600)
                now = datetime.datetime.now()
                target_time = now.replace(hour=10, minute=0, second=0, microsecond=0)

            wait_time = (target_time - now).total_seconds()
            await asyncio.sleep(wait_time)

            if channel:
                try:
                    today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
                    await channel.send(f"📘 **EE Weekly Macro Recap – {today_str}**\nHere's a look at the major trends over the past week:")
                    charts, summary = generate_weekly_charts()
                    for file_path, caption in charts:
                        await channel.send(file=discord.File(file_path))
                        await asyncio.sleep(1.1)
                        await channel.send(caption)
                        await asyncio.sleep(1.1)
                    if summary:
                        await channel.send(summary)
                except Exception as e:
                    print(f"❌ Error sending weekly report: {e}")

            await asyncio.sleep(86400)

bot = MacroBot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"📋 Bot is in {len(bot.guilds)} servers")
    for guild in bot.guilds:
        print(f"Server: {guild.name}")
        for channel in guild.text_channels:
            print(f"  - #{channel.name} (ID: {channel.id})")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "!test":
        await message.channel.send("📊 Macro Bot is online and working!")

    if message.content.lower() == "!post":
        try:
            today_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            await message.channel.send(f"📅 **EE Daily Macro Report – {today_str}**\nHere’s today’s snapshot of key macro ratios and breakouts.")
            results, summary = generate_all_charts()
            for file_path, caption in results:
                await message.channel.send(file=discord.File(file_path))
                await asyncio.sleep(1.1)
                await message.channel.send(caption)
                await asyncio.sleep(1.1)
            if summary:
                await message.channel.send(summary)
        except Exception as e:
            print(f"❌ Error during !post: {e}")
            await message.channel.send("⚠️ Failed to generate or send the charts.")

    if message.content.lower() == "!status":
        current_time = datetime.datetime.now()
        target_time = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
        if current_time > target_time:
            target_time += datetime.timedelta(days=1)
        wait_time = (target_time - current_time).total_seconds()
        hours, remainder = divmod(int(wait_time), 3600)
        minutes, seconds = divmod(remainder, 60)

        status_message = (
            f"**Bot Status**\n"
            f"• Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• Next daily post: {target_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• Time until post: {hours}h {minutes}m {seconds}s\n"
            f"• Channel ID: {CHANNEL_ID}\n"
            f"• Test mode: {TEST_MODE}"
        )
        await message.channel.send(status_message)

try:
    print("🔄 Starting bot...")
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    print("❌ Invalid Discord token. Check DISCORD_TOKEN env variable.")
except Exception as e:
    print(f"❌ Bot startup error: {e}")
