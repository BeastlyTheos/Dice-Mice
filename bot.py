#!/usr/bin/python3
import discord
from dotenv import load_dotenv
import logging
import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Alias
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

engine = create_engine('sqlite:///db/db.sqlite3')
Session = sessionmaker(bind=engine)

aliasRegex = re.compile(r'\s*(?P<name>\w+)?\s*(?P<equals>=)?\s*(?P<definition>.*)')


@client.event
async def on_ready():
	print("connected.")


@client.event
async def on_message(msg):
	try:
		if msg.author == client.user:
			return "own message"
		if msg.content.startswith("!"):
			command = msg.content[1:]
			reply = handleCommand(msg, command)
		elif diceRegex.search(msg.content):
			res = parser.parse(msg.content)
			reply = f"{msg.author.display_name} -- {res}"
		else:
			return "no dice"

		if reply:
			await msg.channel.send(reply)
	except Exception as e:
		log.error(
			f"{repr(e)} when handling on_message event with content {repr(msg.content)} from {msg.author.display_name}."
		)


def handleCommand(msg, command):
	commandName, args = parseCommand(command)
	if commandName in COMMANDS:
		return COMMANDS[commandName](msg, args)
	else:
		return None


def parseCommand(command):
	command = command.strip()
	try:
		commandName = command[:command.index(' ')]
	except ValueError:
		commandName = command
	args = command[len(commandName):].strip()
	return commandName, args


def handleAlias(msg, args):
	name, isDefining, definition = parseAlias(args)
	session = Session()
	if definition:
		alias = Alias(user=msg.author.user, name=name, definition=definition)
		session.add(alias)
		session.commit()


def parseAlias(args):
	m = aliasRegex.match(args)
	isDefining = m.group('equals') or m.group('definition')
	return m.group('name'), isDefining, m.group('definition')


COMMANDS = dict(
	alias=handleAlias,
)

if __name__ == '__main__':
	client.run(TOKEN)
