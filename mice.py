#!/usr/bin/python3.8
import logging
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Alias
from DiceParser import parser, lexerRegexFlags, t_DIE

diceRegex = re.compile(t_DIE.__doc__, flags=lexerRegexFlags)
aliasRegex = re.compile(r'\s*(?P<name>\w+)?\s*(?P<equals>=)?\s*(?P<definition>.*)')

log = logging.getLogger(__name__)

engine = create_engine('sqlite:///db/db.sqlite3')
Session = sessionmaker(bind=engine)


def handleInput(author, text):
	if text.startswith("!"):
		command = text[1:]
		return handleCommand(author, text, command)
	elif diceRegex.search(text):
		res = parser.parse(text)
		return f"{author.display_name} -- {res}"


def handleCommand(author, text, command):
	commandName, args = parseCommand(command)
	log.debug(f"Executing {commandName=}({args=})")
	if commandName in COMMANDS:
		return COMMANDS[commandName](author, text, args)
	else:
		session = Session()
		for alias in session.query(Alias).filter_by(user=author.id):
			if alias.name == commandName:
				return f"{author.display_name} -- {parser.parse(alias.definition)}"
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


def handleAlias(author, text, args):
	name, isDefining, definition = parseAlias(args)
	log.debug(f"Alias command called with {name=}, {isDefining=}, {definition=}")
	session = Session()
	if not name:
		aliases = session.query(Alias).filter_by(user=author.id)
		if aliases.count():
			reply = [f"{author.display_name} has the following aliases defined:"]
			for alias in aliases:
				reply.append(f"{alias.name} = {alias.definition}")
			reply = "\n".join(reply)
		else:
			reply = f'{author.display_name} has no aliases defined. Type "!alias <shorthand>=<text>" to define an alias.'
	elif not isDefining:
		res = session.query(Alias).filter_by(user=author.id, name=name)
		if res.count():
			alias = res[0]
			return f"{author.display_name} -- {alias.name} is aliased to {alias.definition}"
		else:
			reply = f"{author.display_name} -- {name} is not aliased to anything."
	elif not definition:
		res = session.query(Alias).filter_by(user=author.id, name=name)
		if res.count():
			alias = res[0]
			res.delete()
			session.commit()
			return f"{author.display_name} -- {name} is no longer aliased to {alias.definition}"
		else:
			reply = f"{author.display_name} -- {name} is not aliased to anything."
	elif definition:
		alias = Alias(user=author.id, name=name, definition=definition)
		session.add(alias)
		session.commit()
		reply = f"stored alias for {author.display_name} = {definition}"
	log.debug(f"{reply=}")
	return reply


def parseAlias(args):
	m = aliasRegex.match(args)
	isDefining = m.group('equals') or m.group('definition')
	return m.group('name'), isDefining, m.group('definition')


COMMANDS = dict(
	alias=handleAlias,
)
