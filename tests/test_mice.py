from collections import namedtuple
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
from unittest.mock import Mock

import mice
from mice import (
	handleInput,
	COMMANDS,
	handleCommand,
	parseCommand,
	handleAlias,
	Alias,
)

Author = namedtuple("Author", "id display_name")
mice.engine = create_engine('sqlite:///:memory:')
mice.Session = sessionmaker(bind=mice.engine)
Alias.metadata.create_all(mice.engine)


class Test_handleInput(unittest.TestCase):
	def test_doesNothing_whenMessageHasNoDice(self):
		author = Author(0, "a user wanting to talk")
		for text in (
			"hello world",
			"indi12",
			"4+4d",
			"",
			"d\n67",
		):
			reply = handleInput(author, text)
			self.assertFalse(reply)

	def test_sendsReply_whenMessageContainsDiceCodes(self):
		author = Author(0, "someone who is on a roll")
		for text in (
			"d20",
			"Hello d20dis world",
			"hit for d20adv+3 then d6+2 damage.",
			"d8\nd9+4",
			"hello\nthere\nd2",
		):
			reply = handleInput(author, text)
			self.assertTrue(reply)
			self.assertNotEqual(reply, "no dice")


class Test_handleCommand(unittest.TestCase):
	def test_delegatesToCorrectHandler(self):
		msg = Mock(name="msg")

		for name in COMMANDS:
			COMMANDS[name] = Mock(name=name)

		for content, name in (
			("alias", "alias"),
			("  alias = ", "alias"),
			("\talias hw = hello world", "alias"),
		):
			name, args = parseCommand(content)
			handleCommand(msg.author, msg.content, content)
			COMMANDS[name].assert_called_with(msg.author, msg.content, args)
			COMMANDS[name].reset()

	def test_returnsNothing_whenInvokedWithInvalidCommand(self):
		msg = Mock()
		msg.author.id = -1
		for command in (
			"wrongcommand",
			"hello world",
			"alais",
			"ailas",
			"None",
			" \t",
			"",
		):
			reply = handleCommand(msg.author, msg.content, command)
			self.assertFalse(reply, f"Returned {reply} when issuing invalid {command=}")


class Test_handleAlias(unittest.TestCase):
	def tearDown(self):
		session = mice.Session()
		session.query(Alias).delete()

	def test_storesAlias_whenDefinedByUser(self):
		msg = Mock()
		session = mice.Session()
		for userId, content, name, definition in (
			(0, "slam = slams for d6", "slam", "slams for d6"),
			(86400, "rapier = d20adv + 5 then hit for d8", "rapier", "d20adv + 5 then hit for d8"),
		):
			msg.author.display_name = "Bob"
			msg.author.id = userId
			reply = handleAlias(msg.author, msg.content, content)
			self.assertEqual(reply, f"stored alias for {msg.author.display_name} = {definition}")
			res = session.query(Alias).filter_by(user=userId, name=name)
			self.assertEqual(res.count(), 1)
			self.assertEqual(res[0].definition, definition)

	def test_showsAlias_ifExists(self):
		msg = Mock()
		session = mice.Session()
		for authorName, authorId, content, name, definition in (
			("Bill", 0, "slam", "slam", "slams for d6"),
			("Bert", 86400, " rapier ", "rapier", "d20adv + 5 then hit for d8"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			session.add(Alias(user=authorId, name=name, definition=definition))
			session.commit()
			reply = handleAlias(msg.author, msg.content, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is aliased to {definition.strip()}")

	def test_givenNameDoesNotExist_whenDefinitionNotSpecified_thenReplyWithError(self):
		msg = Mock()
		for authorName, authorId, content, name in (
			("Bill", 0, "slam", "slam"),
			("Bert", 86400, " rapier ", "rapier"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			reply = handleAlias(msg.author, msg.content, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is not aliased to anything.")

	def test_givenAliasExists_whenDefinitionNotSpecified_thenDelete(self):
		msg = Mock()
		session = mice.Session()
		for authorName, authorId, content, name, definition in (
			("Bill", 0, "slam=", "slam", "slams for d6"),
			("Bert", 86400, " rapier = ", "rapier", "d20adv + 5 then hit for d8"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			session.add(Alias(user=authorId, name=name, definition=definition))
			session.commit()
			reply = handleAlias(msg.author, msg.content, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is no longer aliased to {definition.strip()}")

	def test_givenAliasDoesNotExists_whenDefinitionNotSpecified_thenReplyWithError(self):
		msg = Mock()
		for authorName, authorId, content, name in (
			("fBill", 0, "slam=", "slam"),
			("Bert", 86400, " rapier = ", "rapier"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			reply = handleAlias(msg.author, msg.content, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is not aliased to anything.")

	def test_whenNoArgumentsGiven_thenPrintAllAliases(self):
		session = mice.Session()
		msg = Mock()
		msg.author.id = 21027
		msg.author.display_name = "Dymorius"
		expectedHeader = f"{msg.author.display_name} has the following aliases defined:"
		expectedAliases = []
		for content, name, definition in (
			("", "slam", "slams for d6"),
			(" ", "rapier", "d20adv + 5 then hit for d8"),
		):
			expectedAliases.append(f"{name} = {definition.strip()}")
			expectedAliases.sort()
			session.add(Alias(user=msg.author.id, name=name, definition=definition))
			session.commit()

			reply = handleAlias(msg.author, msg.content, content)

			aliases = reply.split("\n")[1:]
			aliases.sort()
			self.assertEqual(reply.split("\n")[0], expectedHeader)
			self.assertListEqual(aliases, expectedAliases)

	def test_whenNoArgumentsGiven_andNoAliasesDefined_thenPrintUserHasNoAliases(self):
		msg = Mock()
		msg.author.id = 21027
		msg.author.display_name = "Dymorius"
		expectedOutput = f'{msg.author.display_name} has no aliases defined.'

		reply = handleAlias(msg.author, msg.content, "")

		self.assertTrue(reply.startswith(expectedOutput), f"{reply=} does not start with {expectedOutput=}")

	def test_whenCommandIsAnAlias_thenParseDefinition(self):
		msg = Mock()
		session = mice.Session()
		for authorName, authorId, name, definition, definitionRegex in (
			("Bill", 0, "slam", "slams for d6", r"slams for \d"),
			("Bert", 86400, "rapier", "d20adv + 5 then hit for d8", r"\[\d{1,2}, \d{1,2}\] \+ 5 = \d{1,2} then hit for \d"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			session.add(Alias(user=authorId, name=name, definition=definition))
			session.commit()

			reply = handleCommand(msg.author, msg.content, name)

			expectedReply = f"{authorName} -- {definitionRegex}"
			self.assertTrue(reply, f"Alias {name} was not executed")
			self.assertTrue(re.match(expectedReply, reply), f"{reply=} does not match desired {expectedReply=}")
