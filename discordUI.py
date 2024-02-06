#! /usr/bin/python3.8
import argparse
import discord
from dotenv import load_dotenv
import logging
import os
from sys import stdout

from DiceParser import ParserTimeoutError
import DiceParser
from mice import handleInput

GUILD_GREETING = """
I am your dice mice, ready to roll.
Just type your dice codes, and I'll echo your message back with the dice already rolled.
For more help, check out https://github.com/BeastlyTheos//Dice-Mice
"""

argparser = argparse.ArgumentParser()
argparser.add_argument(
	'-v', "--verbose",
	action='count', default=0,
	help="Increase the output verbosity. Can be used up to 3 times.",
)
args = argparser.parse_args()

logging.basicConfig(
	level=40 - 10 * args.verbose,
	filename="log.log",
	format="{levelname} from {name}. {message} on {asctime}. In {filename}, {funcName} line {lineno}",
	datefmt="%b %d %H:%M",
	style="{",
)
log = logging.getLogger("main")
log.addHandler(logging.StreamHandler(stdout))

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
client = discord.Client()


@client.event
async def on_ready():
	print("connected.")


@client.event
async def on_guild_join(guild):
	log.info(f"joinned {guild.name=}")
	channel = guild.system_channel
	if channel:
		log.debug("has system channel")
	else:
		log.debug("does not have system channel")
		channel = guild.text_channels[0]
	await channel.send(GUILD_GREETING)
	log.info(f"sent greeting to {channel.name=}")


@client.event
async def on_message(msg):
	try:
		if msg.author == client.user:
			return "own message"
		log.info(f"Received {msg.content=} from {msg.author.display_name}")
		DiceParser.currentName = msg.author.display_name
		reply = handleInput(msg.author, msg.content)
		if reply:
			await msg.channel.send(reply)
		else:
			return "no dice"
	except ParserTimeoutError as e:
		await msg.channel.send(
			f"{msg.author.display_name} -- Sorry. Those dice rolls are too big and complex for our little mice hands"
		)
		log.warning(
			f"{repr(e)} when handling on_message event with content {repr(msg.content)} from {msg.author.display_name}."
		)
		raise e
	except Exception as e:
		log.error(
			f"{repr(e)} when handling on_message event with content {repr(msg.content)} from {msg.author.display_name}."
		)

if __name__ == '__main__':
	client.run(TOKEN)
