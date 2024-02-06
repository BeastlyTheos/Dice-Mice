from asyncio import run
import logging
import unittest
from unittest.mock import AsyncMock, Mock

import discordUI
from discordUI import (
	on_guild_join,
	GUILD_GREETING,
	on_message,
	ParserTimeoutError,
)


class Test_on_guild_join(unittest.IsolatedAsyncioTestCase):
	async def test_ifGuildHasSystemChannel_whenJoining_thenSendGreetingToSystemChannel(self):
		guild = Mock()
		guild.system_channel = Mock()
		guild.system_channel.name = "test system channel"
		guild.system_channel.send = AsyncMock()
		await on_guild_join(guild)
		guild.system_channel.send.assert_called_with(GUILD_GREETING)

	async def test_whenJoiningGuild_thenInfoMessageIsLogged(self):
		guild = Mock()
		guild.name = "logger's guild"
		channel = Mock()
		channel.name = "dumb channel"
		channel.send = AsyncMock()
		guild.system_channel = channel
		with self.assertLogs("main", logging.INFO) as logs:
			await on_guild_join(guild)
			self.assertEqual(logs.output[0], f"INFO:main:joinned {guild.name=}")
			self.assertEqual(logs.output[1], f"INFO:main:sent greeting to {channel.name=}")


class Test_on_message(unittest.TestCase):
	def test_doesNothing_whenMessageIsFromSelf(self):
		discordUI.client = Mock()
		msg = Mock()
		msg.author = discordUI.client.user = Mock()
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

	def test_ifTimelimitExceeded_whileProcessingMessage_thenAbortMessage(self):
		msg = AsyncMock()
		msg.content = "1000000d1000000h1"
		msg.channel.send = AsyncMock()
		msg.author.display_name = "bert"
		with self.assertLogs("main", logging.WARNING):
			with self.assertRaises(ParserTimeoutError):
				run(on_message(msg))
		msg.channel.send.assert_called()
