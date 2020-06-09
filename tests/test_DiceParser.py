import re
import unittest

from DiceParser import (
	lexer, parser,
	p_numeric2DIE,
)


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
			('Hello world', r'Hello world'),
			('d20', r'\d{1,2}'),
			(' d20', r' \d{1,2}'),
			('d20 ', r'\d{1,2} '),
			(' d20 ', r' \d{1,2} '),
			('Hello D7 world', r'Hello \d world'),
			('attacks for d20 then d8 damage.', r'attacks for \d{1,2} then \d damage.'),
			('d0', r'd0'),
			('Tries a trivial D0 roll', r'Tries a trivial D0 roll'),
			('mixes textandrollsd8d', r'mixes textandrollsd8d'),
			('d4then anotherd20 d4roll', r'\dthen anotherd20 \droll'),
		):
			res = parser.parse(data)
			self.assertTrue(res, f'failed to parse `{data}`')
			self.assertEqual(type(res), str)
			self.assertTrue(
				re.match(expectedRegexp, res),
				f'The data {data} was parsed into `{res}`, which does not match `{expectedRegexp}`'
			)


class TestParseFunctions(unittest.TestCase):
	def test_numeric2DIE(self):
		for token in (
			dict(numDice=1, numSides=20),
			dict(numDice=1, numSides=8),
			dict(numDice=1, numSides=2),
			dict(numDice=1, numSides=1),
			dict(numDice=2, numSides=20),
			dict(numDice=2, numSides=8),
			dict(numDice=2, numSides=2),
			dict(numDice=2, numSides=1),
			dict(numDice=12, numSides=20),
			dict(numDice=12, numSides=8),
			dict(numDice=12, numSides=2),
			dict(numDice=12, numSides=1),
			dict(numDice=0, numSides=20),
			dict(numDice=0, numSides=8),
			dict(numDice=0, numSides=2),
			dict(numDice=0, numSides=1),
		):
			p = [None, token]
			p_numeric2DIE(p)
			res = int(p[0]['result'])
			min = token['numDice']
			max = token['numDice'] * token['numSides']
			self.assertTrue(min <= res <= max, f"The token {token} produced {res}.")
