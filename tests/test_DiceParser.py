import re
import unittest

from DiceParser import (
	lexer, parser,
	HIGHEST, LOWEST,
	p_expr2numeric,
	p_numeric2DIE,
	p_numeric2PLUSMINUS,
)


class TestLexer(unittest.TestCase):
	def test_diceTokenising(self):
		for data, numDice, numSides, range, rangeSize in (
			("d20", 1, 20, HIGHEST, 1),
			("d8", 1, 8, HIGHEST, 1),
			("D8", 1, 8, HIGHEST, 1),
			("2d20", 2, 20, HIGHEST, 2),
			("9d8", 9, 8, HIGHEST, 9),
			("10D8", 10, 8, HIGHEST, 10),
			("0d10", 0, 10, HIGHEST, 0),
			("2d20kh1", 2, 20, HIGHEST, 1),
			("3d20kh1", 3, 20, HIGHEST, 1),
			("4d6kl3", 4, 6, LOWEST, 3),
			("8d20DH5", 8, 20, LOWEST, 3),
			("1d20DL1", 1, 20, HIGHEST, 0),
			("3d20k1", 3, 20, HIGHEST, 1),
			("4d6k3", 4, 6, HIGHEST, 3),
			("8d20D5", 8, 20, HIGHEST, 3),
			("1d20D1", 1, 20, HIGHEST, 0),
			("3d20h1", 3, 20, HIGHEST, 1),
			("4d6l3", 4, 6, LOWEST, 3),
			("8d20H5", 8, 20, HIGHEST, 5),
			("1d20L1", 1, 20, LOWEST, 1),
			("3d201", 3, 201, HIGHEST, 3),
			("4d63", 4, 63, HIGHEST, 4),
			("8d205", 8, 205, HIGHEST, 8),
			("1d201", 1, 201, HIGHEST, 1),
			("3d20kh", 3, 20, HIGHEST, 1),
			("4d6kl", 4, 6, LOWEST, 1),
			("8d20DH", 8, 20, LOWEST, 7),
			("1d20DL", 1, 20, HIGHEST, 0),
			("3d20k", 3, 20, HIGHEST, 1),
			("4d6k", 4, 6, HIGHEST, 1),
			("8d20D", 8, 20, HIGHEST, 7),
			("1d20D", 1, 20, HIGHEST, 0),
			("3d20k", 3, 20, HIGHEST, 1),
			("4d6k", 4, 6, HIGHEST, 1),
			("8d20D", 8, 20, HIGHEST, 7),
			("1d20D", 1, 20, HIGHEST, 0),
			("1d20D8", 1, 20, HIGHEST, 0),
			("4d6k12", 4, 6, HIGHEST, 4),
			("d20adv", 2, 20, HIGHEST, 1),
			("d20dis", 2, 20, LOWEST, 1),
			("3d6AdV", 4, 6, HIGHEST, 3),
			("0d20dis", 1, 20, LOWEST, 0),
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
			self.assertEqual(
				tok.value['range'], range,
				"Token for {data} includes the {range} dice in its sum, but should include the {expected}.".format(
					data=data,
					range="HIGHEST" if tok.value['range'] == HIGHEST else "lowest",
					expected="HIGHEST" if range == HIGHEST else "lowest",
				)
			)
			self.assertEqual(
				tok.value['rangeSize'], rangeSize,
				f"Token for {data} includes {tok.value['rangeSize']} dice in its sum, but should have {rangeSize} dice."
			)
			tok = lexer.token()
			self.assertFalse(tok, f"When tokenising {data} multiple tokens were returned.")

	def test_diceTokenising_excludesNonDiceText(self):
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
			('trying to negate a roll -d4', 'trying to negate a roll -'),
			('trying to roll a negative number of times -2d8.', 'trying to roll a negative number of times -.'),
			('lowest\n d20l3', 'lowest\n '),
			('lowest\n d\n20l3', 'lowest\n d\n20l3'),
			('lowest d20\nd3', 'lowest \n'),
			('h-d45h8.', 'h-.'),
			('3 d12kk ', '3 k '),
			('then d4dk4', 'then k4'),
			('and 4d8kl1 hits', 'and  hits'),
			('d20adv', ''),
			('3d4dis stats', ' stats'),
			('t d20dishit', 't hit'),
		):
			lexer.input(data)

			plaintext = ''
			for tok in lexer:
				if tok.type == "DIE":
					continue
				plaintext += str(tok.value)
			self.assertEqual(plaintext, expectedPlaintext)

	def test_numericTokens(self):
		for text, value in (
			('0', 0),
			('4', 4),
			('92', 92),
			('00', 0),
			('04', 4),
			('8.4', 8.4),
			('9.223', 9.223),
		):
			lexer.input(text)
			tok = lexer.token()
			self.assertEqual(tok.value, value, f"text is `{text}`")

	def test_operandTokens(self):
		for text, type in (
			('+', 'PLUS'),
			(' +', 'PLUS'),
			(' +\t', 'PLUS'),
			('-', 'MINUS'),
			(' - ', 'MINUS'),
			(' -', 'MINUS'),
			('*', 'MULTIPLY'),
			(' *', 'MULTIPLY'),
			('* ', 'MULTIPLY'),
			('  *  ', 'MULTIPLY'),
			('/', 'DIVIDE'),
			(' /', 'DIVIDE'),
			('/ ', 'DIVIDE'),
			('  /  ', 'DIVIDE'),
		):
			lexer.input(text)
			tok = lexer.token()
			self.assertEqual(tok.type, type, f"text is `{text}`")


class TestParser(unittest.TestCase):
	def test_DiceParsing(self):
		for data, expectedValues in (
			("d20", 20),
			("d8", [8]),
			("D8", [8]),
		):
			res = parser.parse(data)
			numSides = int(data[1:])
			self.assertTrue(1 <= int(res) <= numSides)

	def test_parsingInputWithoutDiceCodes(self):
		for data, expectedOutput in (
			('Hello world', 'Hello world'),
			('d0', 'd0'),
			('Tries a trivial D0 roll', 'Tries a trivial D0 roll'),
			('mixes textandrollsd8d', 'mixes textandrollsd8d'),
			('0d0', '0d0'),
			('1+1', '1+1 = 2'),
			('\t2+8', '\t2+8 = 10'),
			('98 +42+ 38', '98 +42+ 38 = 178'),
			('1-1', '1-1 = 0'),
			('4 -9', '4 -9 = -5'),
			(' 18- 3', ' 18- 3 = 15'),
			('stand-alone dash', 'stand-alone dash'),
			('ctrl+alt-delete', 'ctrl+alt-delete'),
			('4+8-3', '4+8-3 = 9'),
			('4-8+3', '4-8+3 = -1'),
		):
			res = parser.parse(data)
			self.assertTrue(res, f'failed to parse `{data}`')
			self.assertEqual(type(res), str)
			self.assertEqual(
				expectedOutput, res,
				f'The data `{data}` was parsed into\n`{res}`,\nwhich does not match the regexp\n`{expectedOutput}`'
			)

	def test_parsingInputWithDiceCodes(self):
		for data, expectedRegexp in (
			('d20', r'\d{1,2}'),
			(' d20', r' \d{1,2}'),
			('d20 ', r'\d{1,2} '),
			(' d20 ', r' \d{1,2} '),
			('Hello D7 world', r'Hello \d world'),
			('attacks for d20 then d8 damage.', r'attacks for \d{1,2} then \d damage.'),
			('d4then anotherd20 d4roll', r'\dthen anotherd20 \droll'),
			('2d20', r'\[\d{1,2}, \d{1,2}\] = \d{1,2}'),
			(' 49d20 ', r' \[\d{1,2}(, \d{1,2}){48}\] = \d{1,3} '),
			('attacks for 0d20 then 1d8 damage.', r'attacks for \[] then \d damage.'),
			('modify then subtract a roll 9-d8', r'modify then subtract a roll 9-\d = \d'),
			('modify then subtract a roll 2-3d8', r'modify then subtract a roll 2-\[\d, \d, \d] = -\d{1,2}'),
			('trying to ne+gate -a roll -d4', r'trying to ne\+gate -a roll -\d'),
			('rolling a negative number of times -2d8.', r'rolling a negative number of times -\[\d, \d] = \d{1,2}.'),
			('d20adv', r'\[\d{1,2}, \d{1,2}\] = \d{1,2}'),
			('d20dis', r'\[\d{1,2}, \d{1,2}\] = \d{1,2}'),
			('3d6adv', r'\[\d(, \d){3}\] = \d{1,2}'),
		):
			res = parser.parse(data)
			self.assertTrue(res, f'failed to parse `{data}`')
			self.assertEqual(type(res), str)
			self.assertTrue(
				re.match(expectedRegexp, res),
				f'The data `{data}` was parsed into\n`{res}`,\nwhich does not match the regexp\n`{expectedRegexp}`'
			)


class TestParseFunctions(unittest.TestCase):
	def test_expr2numeric(self):
		for token, expectedOutput in (
			(dict(result=17, text='17'), '17'),
			(dict(result=5, text='5'), '5'),
			(dict(result=2, text='2'), '2'),
			(dict(result=1, text='1'), '1'),
			(dict(result=37, text='[19, 18]'), '[19, 18] = 37'),
			(dict(result=106, text='[8, 17, 3, 15, 10, 11, 5, 9, 19]'), '[8, 17, 3, 15, 10, 11, 5, 9, 19] = 106'),
			(dict(result=0, text='[]'), '[]'),
			(dict(text='1+1', result=2), '1+1 = 2'),
			(dict(text='1-1', result=0), '1-1 = 0'),
			(dict(text='19- 5', result=14), '19- 5 = 14'),
			(dict(text='1- 4', result=-3), '1- 4 = -3'),
		):
			p = [None, token]
			p_expr2numeric(p)
			self.assertEqual(
				p[0], expectedOutput,
				f"The token {token} produced `{p[0]}`, but was expecting `{expectedOutput}`."
			)

	def test_numeric2PLUSMINUS(self):
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
			(
				dict(text='[11, 5]', result=16),
				' -',
				dict(text='3', result=3),
			),

		):
			p = [None, prev, cur, next]
			p_numeric2PLUSMINUS(p)
			self.assertEqual(p[0]['result'], prev['result'] + next['result'])
			self.assertEqual(p[0]['text'], prev['text'] + cur + next['text'])

	def test_numeric2DIE(self):
		for token in (
			dict(numDice=1, numSides=2, range=HIGHEST, rangeSize=1),
			dict(numDice=1, numSides=8, range=HIGHEST, rangeSize=1),
			dict(numDice=1, numSides=2, range=HIGHEST, rangeSize=1),
			dict(numDice=1, numSides=1, range=HIGHEST, rangeSize=1),
			dict(numDice=2, numSides=2, range=HIGHEST, rangeSize=2),
			dict(numDice=2, numSides=8, range=HIGHEST, rangeSize=2),
			dict(numDice=2, numSides=2, range=HIGHEST, rangeSize=2),
			dict(numDice=2, numSides=1, range=HIGHEST, rangeSize=2),
			dict(numDice=12, numSides=2, range=HIGHEST, rangeSize=12),
			dict(numDice=12, numSides=8, range=HIGHEST, rangeSize=12),
			dict(numDice=12, numSides=2, range=HIGHEST, rangeSize=12),
			dict(numDice=12, numSides=1, range=HIGHEST, rangeSize=12),
			dict(numDice=0, numSides=2, range=HIGHEST, rangeSize=0),
			dict(numDice=0, numSides=8, range=HIGHEST, rangeSize=0),
			dict(numDice=0, numSides=2, range=HIGHEST, rangeSize=0),
			dict(numDice=0, numSides=1, range=HIGHEST, rangeSize=0),
			dict(numDice=1, numSides=2, range=LOWEST, rangeSize=1),
			dict(numDice=1, numSides=8, range=LOWEST, rangeSize=1),
			dict(numDice=1, numSides=2, range=LOWEST, rangeSize=1),
			dict(numDice=1, numSides=1, range=LOWEST, rangeSize=1),
			dict(numDice=2, numSides=2, range=LOWEST, rangeSize=2),
			dict(numDice=2, numSides=8, range=LOWEST, rangeSize=2),
			dict(numDice=2, numSides=2, range=LOWEST, rangeSize=2),
			dict(numDice=2, numSides=1, range=LOWEST, rangeSize=2),
			dict(numDice=12, numSides=2, range=LOWEST, rangeSize=12),
			dict(numDice=12, numSides=8, range=LOWEST, rangeSize=12),
			dict(numDice=12, numSides=2, range=LOWEST, rangeSize=12),
			dict(numDice=12, numSides=1, range=LOWEST, rangeSize=12),
			dict(numDice=0, numSides=2, range=LOWEST, rangeSize=0),
			dict(numDice=0, numSides=8, range=LOWEST, rangeSize=0),
			dict(numDice=0, numSides=2, range=LOWEST, rangeSize=0),
			dict(numDice=0, numSides=1, range=LOWEST, rangeSize=0),
			dict(numDice=1, numSides=2, range=HIGHEST, rangeSize=0),
			dict(numDice=1, numSides=8, range=LOWEST, rangeSize=0),
			dict(numDice=2, numSides=2, range=HIGHEST, rangeSize=1),
			dict(numDice=2, numSides=8, range=LOWEST, rangeSize=0),
			dict(numDice=2, numSides=2, range=HIGHEST, rangeSize=0),
			dict(numDice=2, numSides=1, range=LOWEST, rangeSize=1),
			dict(numDice=12, numSides=2, range=HIGHEST, rangeSize=6),
			dict(numDice=12, numSides=8, range=LOWEST, rangeSize=4),
			dict(numDice=12, numSides=2, range=HIGHEST, rangeSize=11),
			dict(numDice=12, numSides=1, range=LOWEST, rangeSize=1),
		):
			p = [None, token]
			p_numeric2DIE(p)
			res = int(p[0]['result'])
			min = token['rangeSize']
			max = token['rangeSize'] * token['numSides']
			self.assertTrue(min <= res <= max, f"The token {token} produced {res}.")
