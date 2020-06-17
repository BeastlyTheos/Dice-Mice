from asyncio import run
import unittest
from unittest.mock import Mock

import bot
from bot import on_message


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
