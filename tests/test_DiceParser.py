import re
import unittest

from DiceParser import lexer, parser


class TestDiceLexer(unittest.TestCase):
	def test_diceTokens(self):
		for data, numDice, numSides in (
			("d20", 1, 20),
			("d8", 1, 8),
			("D8", 1, 8),
			("2d20", 2, 20),
			("9d8", 9, 8),
			("10D8", 10, 8),
			("0d10", 0, 10),
		):
			lexer.input(data)
			tok = lexer.token()
			self.assertEqual(tok.type, "DIE", f'{data} produces incorrect token type of {tok.type}')
			self.assertEqual(
				tok.value['numDice'], numDice,
				f"Token for {data} has {tok.value['numDice']} dice, but should have {numDice} dice."
			)
			self.assertEqual(
				tok.value['numSides'], numSides,
				f"Token for {data} has {tok.value['numSides']} sides, but should have {numSides} sides."
			)
			tok = lexer.token()
			self.assertFalse(tok, f"When tokenising {data} multiple tokens were returned.")

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


class TestDiceParser(unittest.TestCase):
	def test_simpleDiceParsing(self):
		for data, expectedValues in (
			("d20", 20),
			("d8", [8]),
			("D8", [8]),
		):
			res = parser.parse(data)
			numSides = int(data[1:])
			self.assertTrue(1 <= int(res) <= numSides)

	def test_simpleDiceParsing_withPlaintext(self):
		for data, expectedRegexp in (
			("Hello world", "Hello world"),
			("d20", "(20|10|[1-9]?[1-9])"),
			(" d20", " (20|10|[1-9]?[1-9])"),
			("d20 ", "(20|10|[1-9]?[1-9]) "),
			(" d20 ", " (20|10|[1-9]?[1-9]) "),
			("Hello D7 world", "Hello [1-7] world"),
			('attacks for d20 then d8 damage.', 'attacks for (20|10|[1-9]?[1-9]) then [1-8] damage.'),
			('d0', 'd0'),
			('Tries a trivial D0 roll', 'Tries a trivial D0 roll'),
			('mixes textandrollsd8d', 'mixes textandrollsd8d'),
			('d4then anotherd20 d4roll', '[1-4]then anotherd20 [1-4]roll'),
		):
			res = parser.parse(data)
			self.assertTrue(res, f"failed to parse `{data}`")
			self.assertTrue(
				re.match(expectedRegexp, res),
				f"The data {data} was parsed into `{res}`, which does not match `{expectedRegexp}`"
			)
