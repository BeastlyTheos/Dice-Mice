import os
import re


import discord
from dotenv import load_dotenv

from DiceParser import parser, t_DIE
diceRegexp = re.compile(t_DIE.__doc__)

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
		return
	if not diceRegexp.search(msg.content):
		return

	res = parser.parse(msg.content)
	await msg.channel.send(f"{msg.author.display_name} -- {res}")

client.run(TOKEN)
