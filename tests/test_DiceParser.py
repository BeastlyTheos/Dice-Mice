import unittest

from DiceParser import lexer


class TestDiceParser(unittest.TestCase):
	def test_simpleDiceTokens(self):
		for data, expectedValues in (
			("d20", [20]),
			("d8", [8]),
			("D8", [8]),
			("D0", [0]),
		):
			lexer.input(data)
			for tok in lexer:
				self.assertEqual(
					tok.value['numSides'], expectedValues[0],
					f"Token for {data} has {tok.value['numSides']} sides, but should have {expectedValues[0]} sides."
				)
