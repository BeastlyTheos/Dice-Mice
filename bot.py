#!/usr/bin/python3
import logging
import os
import re

import discord
from dotenv import load_dotenv

from DiceParser import parser, lexerRegexFlags, t_DIE
diceRegex = re.compile(t_DIE.__doc__, flags=lexerRegexFlags)

logging.basicConfig(
	level=logging.ERROR,
	filename="main.log",
	format="{levelname} {message} on {asctime}. In {filename}, {funcName} line {lineno}",
	datefmt="%b %d %H:%M",
	style="{",
)
log = logging.getLogger("main")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()


@client.event
async def on_ready():
	print("connected.")


@client.event
async def on_message(msg):
	try:
		if msg.author == client.user:
			return "own message"
		if not diceRegex.search(msg.content):
			return "no dice"

		res = parser.parse(msg.content)
		await msg.channel.send(f"{msg.author.display_name} -- {res}")
	except Exception as e:
		log.error(
			f"{repr(e)} when handling on_message event with content {repr(msg.content)} from {msg.author.display_name}."
		)

if __name__ == '__main__':
	client.run(TOKEN)
