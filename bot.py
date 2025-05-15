import discord
import os
import asyncio
import datetime
import sys

print("🚀 Starting EE Macro Bot...")
print(f"🕒 Current time: {datetime.datetime.now()}")

# Force output to be sent straight to the console without buffering
# This ensures logs appear in Render console immediately
sys.stdout.reconfigure(line_buffering=True)

TOKEN = os.getenv("DISCORD_TOKEN")
# Use the correct channel ID for #macro-dashboard
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "1372316620093001891"))
# Add a test mode option with a short interval for testing
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
TEST_INTERVAL_MINUTES = int(os.getenv("TEST_INTERVAL_MINUTES", "2"))

print(f"🔑 Using channel ID: {CHANNEL_ID}")
print(f"🧪 Test mode: {TEST_MODE}")

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
        print(f"✅ Bot is ready! Looking for channel with ID: {CHANNEL_ID}")
        channel = self.get_channel(CHANNEL_ID)
        
        if channel:
            print(f"🔗 Successfully connected to channel: #{channel.name}")
        else:
            print(f"❌ ERROR: Could not find channel with ID {CHANNEL_ID}. Check your CHANNEL_ID environment variable.")
            print(f"Available channels: {[ch.name + ' (' + str(ch.id) + ')' for ch in self.get_all_channels()][:5]}")
        
        message_count = 0
        
        while not self.is_closed():
            now = datetime.datetime.now()
            
            if TEST_MODE:
                # In test mode, post a message every few minutes for testing
                wait_time = TEST_INTERVAL_MINUTES * 60
                print(f"🧪 TEST MODE: Will post next message in {TEST_INTERVAL_MINUTES} minutes (at {now + datetime.timedelta(minutes=TEST_INTERVAL_MINUTES)})")
            else:
                # Normal mode - post at 7 AM
                target_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
                
                if now > target_time:
                    target_time += datetime.timedelta(days=1)
                
                wait_time = (target_time - now).total_seconds()
                next_post_time = now + datetime.timedelta(seconds=wait_time)
                print(f"⏳ Waiting {wait_time / 60:.1f} minutes until next macro post at {next_post_time}...")
            
            # Log status every hour while waiting
            if wait_time > 3600:  # If waiting more than an hour
                status_interval = 3600  # Log status every hour
            else:
                status_interval = wait_time / 2  # Log twice during wait period
            
            # Wait until the next post time, but log status periodically
            remaining_wait = wait_time
            while remaining_wait > 0:
                await asyncio.sleep(min(status_interval, remaining_wait))
                remaining_wait -= status_interval
                if remaining_wait > 0:
                    print(f"⌛ Still waiting: {remaining_wait / 60:.1f} minutes left until next post...")
            
            # Time to post!
            message_count += 1
            print(f"📝 Attempting to send message #{message_count} at {datetime.datetime.now()}")
            
            if channel:
                try:
                    await channel.send(f"📊 Good morning. Here's your daily macro update! (Message #{message_count})")
                    print(f"✅ Successfully sent message #{message_count}")
                except Exception as e:
                    print(f"❌ Error sending message: {str(e)}")
            else:
                print(f"❌ Still could not find the channel with ID {CHANNEL_ID}")
                # Try to refresh the channel reference
                channel = self.get_channel(CHANNEL_ID)
                
            # Short sleep to avoid hitting rate limits
            await asyncio.sleep(5)

# ✅ Instantiate Bot
bot = MacroBot(intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"📋 Bot is in {len(bot.guilds)} servers")
    # Print all available channels to help with troubleshooting
    print("Available channels:")
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
    
    # Add a command to force post immediately for testing
    if message.content.lower() == "!post":
        print(f"📣 Received force post command from {message.author}")
        await message.channel.send("📊 Forced macro update! This is a test post.")
    
    # Add a command to display bot status
    if message.content.lower() == "!status":
        print(f"📣 Received status command from {message.author}")
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