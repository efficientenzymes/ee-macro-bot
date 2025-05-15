import discord
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for reading emoji & slash
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!test":
        await message.channel.send("Macro bot is online and ready.")

client.run(TOKEN)
