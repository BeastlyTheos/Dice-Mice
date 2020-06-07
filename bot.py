import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

client = discord.Client()


@client.event
async def on_ready():
	print("connected.")


@client.event
async def on_message(msg):
	if msg.author == client.user:
		print(f"client just said {msg.content}")
		return

	await msg.channel.send(f"You just said {msg.content}")

client.run(TOKEN)
