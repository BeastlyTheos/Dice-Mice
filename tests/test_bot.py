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
