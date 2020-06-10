import re
import unittest

from DiceParser import (
	lexer, parser,
	p_expr2numeric,
	p_numeric2DIE,
	p_numeric2PLUS,
)


class TestLexer(unittest.TestCase):
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
		for data, expectedPlaintext in (
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

			plaintext = ''
			for tok in lexer:
				if tok.type == "DIE":
					continue
				plaintext += str(tok.value)
			self.assertEqual(plaintext, expectedPlaintext)

	def test_numericTokens(self):
		for text, value, type in (
			('0', 0, 'NUMBER'),
			('4', 4, 'NUMBER'),
			('92', 92, 'NUMBER'),
			('00', 0, 'NUMBER'),
			('04', 4, 'NUMBER'),
			('8.4', 8.4, 'NUMBER'),
			('9.223', 9.223, 'NUMBER'),
			('+', '+', 'PLUS'),
			(' +', ' +', 'PLUS'),
			(' +\t', ' +\t', 'PLUS'),
		):
			lexer.input(text)
			tok = lexer.token()
			self.assertEqual(tok.type, type, f"text is `{text}`")
			self.assertEqual(tok.value, value, f"text is `{text}`")


class TestDiceParser(unittest.TestCase):
	def test_DiceParsing(self):
		for data, expectedValues in (
			("d20", 20),
			("d8", [8]),
			("D8", [8]),
		):
			res = parser.parse(data)
			numSides = int(data[1:])
			self.assertTrue(1 <= int(res) <= numSides)

	def test_diceParsing_withPlaintext(self):
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
			('2d20', r'\[\d{1,2}, \d{1,2}\] = \d{1,2}'),
			(' 49d20 ', r' \[\d{1,2}(, \d{1,2}){48}\] = \d{1,3} '),
			('attacks for 0d20 then 1d8 damage.', r'attacks for \[] then \d damage.'),
			('0d0', r'0d0'),
			('1+1', r'1\+1 = 2'),
			('\t2+8', r'\t2\+8 = 10'),
			('98 +42+ 38', r'98 \+42\+ 38 = 178'),
		):
			res = parser.parse(data)
			self.assertTrue(res, f'failed to parse `{data}`')
			self.assertEqual(type(res), str)
			self.assertTrue(
				re.match(expectedRegexp, res),
				f'The data `{data}` was parsed into `{res}`, which does not match the regexp `{expectedRegexp}`'
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

	def test_expr2numeric(self):
		for token, expectedOutput in (
			(dict(result=17, text='17'), '17'),
			(dict(result=5, text='5'), '5'),
			(dict(result=2, text='2'), '2'),
			(dict(result=1, text='1'), '1'),
			(dict(result=37, text='[19, 18]'), '[19, 18] = 37'),
			(dict(result=106, text='[8, 17, 3, 15, 10, 11, 5, 9, 19]'), '[8, 17, 3, 15, 10, 11, 5, 9, 19] = 106'),
			(dict(result=0, text='[]'), '[]'),
			(dict(text='1+1', result=2), '1+1 = 2')
		):
			p = [None, token]
			p_expr2numeric(p)
			self.assertEqual(
				p[0], expectedOutput,
				f"The token {token} produced `{p[0]}`, but was expecting ``{expectedOutput}`."
			)

	def test_numeric2PLUS(self):
		for prev, cur, next in (
			(
				dict(text='1', result=1),
				'+',
				dict(text='1', result=1),
			),
			(
				dict(text=' 94.5\t', result=94.5),
				'  +',
				dict(text='-3 ', result=-3),
			),
		):
			p = [None, prev, cur, next]
			p_numeric2PLUS(p)
			self.assertEqual(p[0]['result'], prev['result'] + next['result'])
			self.assertEqual(p[0]['text'], prev['text'] + cur + next['text'])
