# Dice Parser
# exports a yacc parser that parses dice codes from a string
# dice codes are converted into result codes of the format [{]\d+(, \d+)*[}]([hl]\d+)?
# where the numbers inside the braces are results of a set of rolls
# and the [hl] followed by a number indicates to keep as many highest or lowest rolls

import logging
from ply import lex, yacc
from random import randint
import re

log = logging.getLogger("parser")

lexerRegexFlags = re.DOTALL | re.IGNORECASE | re.UNICODE | re.VERBOSE
HIGHEST, LOWEST = range(2)

tokens = [
	"PLAINTEXT",
	"NUMBER",
	"PLUS",
	"MINUS",
	"MULTIPLY",
	"DIVIDE",
	"DIE",
]

t_PLAINTEXT = r'.+?'
t_MULTIPLY = r'\s*\*\s*'
t_DIVIDE = r'\s*/\s*'
t_PLUS = r'\s*\+\s*'
t_MINUS = r'\s*-\s*'


def t_NUMBER(t):
	r'''
	(?P<num>
		\d+
		(\.\d+)?
	)
	(?!\d*d[1-9])
	'''
	m = t.lexer.lexmatch
	val = m.group('num')
	try:
		t.value = int(val)
	except ValueError:
		t.value = float(val)
	return t


def t_DIE(t):
	r'''
	(?<!\w)
	(?P<numDice>\d+)?
	d(?P<numSides>[1-9]\d*)
	(?P<modifier>
		adv
	|
		dis
	|
		(?P<inclusive>[kd])?(?P<range>[hl])?(?P<rangeSize>\d+)?
	)?
	'''
	data = t.lexer.lexmatch.groupdict()
	data['numDice'] = int(data['numDice']) if data['numDice'] else 1
	data['numSides'] = int(data['numSides'])
	if data['modifier'].lower() == 'adv':
		data['range'] = HIGHEST
		data['rangeSize'] = data['numDice']
		data['numDice'] += 1
	elif data['modifier'].lower() == 'dis':
		data['range'] = LOWEST
		data['rangeSize'] = data['numDice']
		data['numDice'] += 1
	else:
		if data['inclusive'] is None and data['range'] is None:
			data['rangeSize'] = data['numDice']
		data['rangeSize'] = 1 if data['rangeSize'] is None else int(data['rangeSize'])
		if data['inclusive'] and data['inclusive'] in 'Dd':
			data['range'] = LOWEST if data['range'] and data['range'] in 'Hh' else HIGHEST
			data['rangeSize'] = data['numDice'] - data['rangeSize']
		else:
			data['range'] = LOWEST if data['range'] and data['range'] in 'Ll' else HIGHEST
		if data['rangeSize'] < 0:
			data['rangeSize'] = 0
		if data['rangeSize'] > data['numDice']:
			data['rangeSize'] = data['numDice']
	t.value = data
	return t


def t_error(t):
	value = repr(t.value)
	data = repr(t.lexer.lexdata)
	print(f"Error tokenising {value} at position {t.lexpos} in {data}.")
	log.error(f"Unable to tokenise {value} at position {t.lexpos} in {data}.")
	t.lexer.skip(1)


lexer = lex.lex(reflags=lexerRegexFlags)

precedence = (
	('left', 'expr'),
	('left', 'PLAINTEXT'),
	('left', 'numeric'),
	('left', 'PLUS', 'MINUS'),
)


def p_expr2exprexpr(p):
	'expr : expr expr %prec expr'
	p[0] = p[1] + p[2]


def p_expr2PLAINTEXT(p):
	'''expr : PLAINTEXT
	| PLUS
	| MINUS'''
	p[0] = p[1]


def p_expr2numeric(p):
	'expr : numeric %prec numeric'
	text = p[1]['text']
	if text.isdigit() or text == '[]':
		p[0] = text
	else:
		p[0] = f"{p[1]['text']} = {p[1]['result']}"


def p_numeric2PLUSMINUS(p):
	'''numeric : numeric PLUS numeric
	| numeric MINUS numeric'''
	if '-' in p[2]:
		p[3]['result'] *= -1
	text = p[1]['text'] + p[2] + p[3]['text']
	result = p[1]['result'] + p[3]['result']
	p[0] = dict(text=text, result=result)


def p_numeric2NUMBER(p):
	'numeric : NUMBER'
	result = p[1]
	text = str(result)
	p[0] = dict(text=text, result=result)


def p_numeric2DIE(p):
	'numeric : DIE'
	tok = p[1]
	rolls = [randint(1, tok['numSides']) for i in range(tok['numDice'])]
	text = str(rolls[0]) if len(rolls) == 1 else str(rolls)
	rolls.sort()
	max = tok['numDice']
	min = 0
	if tok['range'] == HIGHEST:
		min = tok['numDice'] - tok['rangeSize']
	else:
		max = tok['rangeSize']
	result = sum(rolls[min: max])
	p[0] = dict(result=result, text=text)


def p_expr2error(p):
	'expr : error'
	p[0] = '**<ERROR>**'


def p_error(p):
	value = repr(p.value)
	data = repr(p.lexer.lexdata)
	print(f"Error parsing {p.type} token at position {p.lexpos} in {data}.")
	log.error(f"Unable to parse the token {value} of type {p.type} at position {p.lexpos} in {data}.")


parser = yacc.yacc()
