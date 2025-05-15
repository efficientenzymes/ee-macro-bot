
import discord
import os
import asyncio
import datetime
import sys
from chart_engine import generate_chart

print("🚀 Starting EE Macro Bot...")
print(f"🕒 Current time: {datetime.datetime.now()}")

sys.stdout.reconfigure(line_buffering=True)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1372316620093001891
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
TEST_INTERVAL_MINUTES = int(os.getenv("TEST_INTERVAL_MINUTES", "2"))

print(f"🔑 Using channel ID: {CHANNEL_ID}")
print(f"🧪 Test mode: {TEST_MODE}")

intents = discord.Intents.default()
intents.message_content = True

class MacroBot(discord.Client):
    async def setup_hook(self):
        print("🧠 setup_hook started")
        await asyncio.sleep(2)
        print("🔄 setup_hook scheduling daily task now")
        self.loop.create_task(self.daily_macro_post())

    async def daily_macro_post(self):
        await self.wait_until_ready()
        print(f"✅ Bot is ready! Looking for channel with ID: {CHANNEL_ID}")
        channel = self.get_channel(CHANNEL_ID)

        if channel:
            print(f"🔗 Successfully connected to channel: #{channel.name}")
        else:
            print(f"❌ ERROR: Could not find channel with ID {CHANNEL_ID}.")

        message_count = 0

        while not self.is_closed():
            now = datetime.datetime.now()

            if TEST_MODE:
                wait_time = TEST_INTERVAL_MINUTES * 60
                print(f"🧪 TEST MODE: Will post in {TEST_INTERVAL_MINUTES} minutes.")
            else:
                target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
                if now > target_time:
                    target_time += datetime.timedelta(days=1)
                wait_time = (target_time - now).total_seconds()
                next_post_time = now + datetime.timedelta(seconds=wait_time)
                print(f"⏳ Waiting {wait_time / 60:.1f} minutes until next macro post at {next_post_time}...")

            await asyncio.sleep(wait_time)

            message_count += 1
            print(f"📝 Attempting to send message #{message_count} at {datetime.datetime.now()}")

            if channel:
                try:
                    generate_chart()
                    await channel.send("📊 Good morning! Here's your BTC vs SPX chart:")
                    await channel.send(file=discord.File("btc_vs_spx.png"))
                    print(f"✅ Message #{message_count} sent.")
                except Exception as e:
                    print(f"❌ Error sending message #{message_count}: {str(e)}")
            else:
                print(f"❌ Still could not find the channel with ID {CHANNEL_ID}")
                channel = self.get_channel(CHANNEL_ID)

            await asyncio.sleep(5)

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
        print(f"📣 Received test command from {message.author}")
        await message.channel.send("📊 Macro Bot is online and working!")

    if message.content.lower() == "!post":
        print(f"📣 Received force post command from {message.author}")
        try:
            generate_chart()
            await message.channel.send("📊 Forced macro update! Here's your BTC vs SPX chart:")
            await message.channel.send(file=discord.File("btc_vs_spx.png"))
            print("✅ Chart sent successfully.")
        except Exception as e:
            print(f"❌ Error generating or sending chart: {str(e)}")
            await message.channel.send("⚠️ Failed to generate or send the chart.")

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
            f"• Next scheduled post: {target_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"• Time until next post: {hours}h {minutes}m {seconds}s\n"
            f"• Channel ID set to: {CHANNEL_ID}\n"
            f"• Test mode: {TEST_MODE}"
        )
        await message.channel.send(status_message)

try:
    print("🔄 Starting bot...")
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    print("❌ ERROR: Invalid Discord token. Please check your DISCORD_TOKEN environment variable.")
except Exception as e:
    print(f"❌ ERROR: Failed to start bot: {str(e)}")
