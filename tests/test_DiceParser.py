import unittest

from DiceParser import lexer


class TestDiceParser(unittest.TestCase):
	def test_simpleDiceTokens(self):
		for data, expectedValues in (
			("d20", [20]),
			("d8", [8]),
			("D8", [8]),
		):
			lexer.input(data)
			for tok in lexer:
				self.assertEqual(tok.type, "DIE", f'{data} produces incorrect token type of {tok.type}')
				self.assertEqual(
					tok.value['numSides'], expectedValues[0],
					f"Token for {data} has {tok.value['numSides']} sides, but should have {expectedValues[0]} sides."
				)

	def test_simpleDiceTokens_withPlaintext(self):
		for data, expectedPlaintexts in (
			("Hello world", "Hello world"),
			("d20", ""),
			("\t\td20", "\t\t"),
			("d20 ", " "),
			(" d20\t\t", " \t\t"),
			("Hello D7 world", "Hello  world"),
			('attacks for d20 then d8 damage.', 'attacks for  then  damage.'),
			('d0', 'd0'),
			('Tries a trivial D0 roll', 'Tries a trivial D0 roll'),
			('mixes textandrollsd8d', 'mixes textandrollsd8d'),
			('d4then anotherd20 d4roll', 'then anotherd20 roll'),
		):
			lexer.input(data)

			i = 0
			for tok in lexer:
				if tok.type != "PLAINTEXT":
					continue
				self.assertEqual(
					tok.value, expectedPlaintexts[i],
					f"from string {data}, the {i}th plaintext token is {tok.value}. Expecting {expectedPlaintexts[i]}"
				)
				i += 1
