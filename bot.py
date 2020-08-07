#!/usr/bin/python3
import argparse
import discord
from dotenv import load_dotenv
import logging
import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sys import stdout

from db.models import Alias
from DiceParser import parser, lexerRegexFlags, t_DIE
import DiceParser
diceRegex = re.compile(t_DIE.__doc__, flags=lexerRegexFlags)

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
		log.info(f"Received {msg.content=} from {msg.author.display_name}")
		DiceParser.currentName = msg.author.display_name
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
	log.debug(f"Executing {commandName=}({args=})")
	if commandName in COMMANDS:
		return COMMANDS[commandName](msg, args)
	else:
		session = Session()
		for alias in session.query(Alias).filter_by(user=msg.author.id):
			if alias.name == commandName:
				return f"{msg.author.display_name} -- {parser.parse(alias.definition)}"
	log.debug(f"No command matching {commandName}")
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
	log.debug(f"Alias command called with {name=}, {isDefining=}, {definition=}")
	session = Session()
	if not name:
		reply = [f"{msg.author.display_name} has the following aliases defined:"]
		for alias in session.query(Alias).filter_by(user=msg.author.id):
			reply.append(f"{alias.name} = {alias.definition}")
		reply = "\n".join(reply)
	elif not isDefining:
		res = session.query(Alias).filter_by(user=msg.author.id, name=name)
		if res.count():
			alias = res[0]
			return f"{msg.author.display_name} -- {alias.name} is aliased to {alias.definition}"
		else:
			reply = f"{msg.author.display_name} -- {name} is not aliased to anything."
	elif not definition:
		res = session.query(Alias).filter_by(user=msg.author.id, name=name)
		if res.count():
			alias = res[0]
			res.delete()
			session.commit()
			return f"{msg.author.display_name} -- {name} is no longer aliased to {alias.definition}"
		else:
			reply = f"{msg.author.display_name} -- {name} is not aliased to anything."
	elif definition:
		alias = Alias(user=msg.author.id, name=name, definition=definition)
		session.add(alias)
		session.commit()
		reply = f"stored alias for {msg.author.display_name} = {definition}"
	log.debug(f"{reply=}")
	return reply


def parseAlias(args):
	m = aliasRegex.match(args)
	isDefining = m.group('equals') or m.group('definition')
	return m.group('name'), isDefining, m.group('definition')


COMMANDS = dict(
	alias=handleAlias,
)

if __name__ == '__main__':
	client.run(TOKEN)
