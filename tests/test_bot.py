from asyncio import run
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import unittest
from unittest.mock import AsyncMock, Mock

import bot
from bot import (
	on_message,
	COMMANDS,
	handleCommand,
	parseCommand,
	handleAlias,
	Alias,
)

bot.engine = create_engine('sqlite:///:memory:')
bot.Session = sessionmaker(bind=bot.engine)
Alias.metadata.create_all(bot.engine)


class Test_on_message(unittest.TestCase):
	def test_doesNothing_whenMessageIsFromSelf(self):
		bot.client = Mock()
		msg = Mock()
		msg.author = bot.client.user = Mock()
		res = run(on_message(msg))
		self.assertEqual(res, "own message")

	def test_doesNothing_whenMessageHasNoDice(self):
		msg = Mock()
		for content in (
			"hello world",
			"indi12",
			"4+4d",
			"",
			"d\n67",
		):
			msg.content = content
			res = run(on_message(msg))
			self.assertEqual(res, "no dice")

	def test_sendsReply_whenMessageContainsDiceCodes(self):
		msg = Mock()
		msg.channel.send = AsyncMock()
		for content in (
			"d20",
			"Hello d20dis world",
			"hit for d20adv+3 then d6+2 damage.",
			"d8\nd9+4",
			"hello\nthere\nd2",
		):
			msg.content = content
			run(on_message(msg))
			msg.channel.send.assert_called()

	def test_logsError_whenRaisingException(self):
		with self.assertLogs("main", logging.ERROR):
			run(on_message(Mock(side_effect=Exception("test exception"))))


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
			handleCommand(msg, content)
			COMMANDS[name].assert_called_with(msg, args)
			COMMANDS[name].reset()

	def test_returnsNothing_whenInvokedWithInvalidCommand(self):
		for command in (
			"wrongcommand",
			"hello world",
			"alais",
			"ailas",
			"None",
			" \t",
			"",
		):
			reply = handleCommand(Mock(), command)
			self.assertFalse(reply, f"Returned {reply} when issuing invalid {command=}")


class Test_handleAlias(unittest.TestCase):
	def tearDown(self):
		session = bot.Session()
		session.query(Alias).delete()

	def test_storesAlias_whenDefinedByUser(self):
		msg = Mock()
		session = bot.Session()
		for userId, content, name, definition in (
			(0, "slam = slams for d6", "slam", "slams for d6"),
			(86400, "rapier = d20adv + 5 then hit for d8", "rapier", "d20adv + 5 then hit for d8"),
		):
			msg.author.display_name = "Bob"
			msg.author.id = userId
			reply = handleAlias(msg, content)
			self.assertEqual(reply, f"stored alias for {msg.author.display_name} = {definition}")
			res = session.query(Alias).filter_by(user=userId, name=name)
			self.assertEqual(res.count(), 1)
			self.assertEqual(res[0].definition, definition)

	def test_showsAlias_ifExists(self):
		msg = Mock()
		session = bot.Session()
		for authorName, authorId, content, name, definition in (
			("Bill", 0, "slam", "slam", "slams for d6"),
			("Bert", 86400, " rapier ", "rapier", "d20adv + 5 then hit for d8"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			session.add(Alias(user=authorId, name=name, definition=definition))
			session.commit()
			reply = handleAlias(msg, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is aliased to {definition.strip()}")

	def test_givenNameDoesNotExist_whenDefinitionNotSpecified_thenReplyWithError(self):
		msg = Mock()
		for authorName, authorId, content, name in (
			("Bill", 0, "slam", "slam"),
			("Bert", 86400, " rapier ", "rapier"),
		):
			msg.author.display_name = authorName
			msg.author.id = authorId
			reply = handleAlias(msg, content)
			self.assertEqual(reply, f"{authorName} -- {name.strip()} is not aliased to anything.")
