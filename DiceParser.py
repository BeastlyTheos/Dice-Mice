# Dice Parser
# exports a yacc parser that parses dice codes from a string
# dice codes are converted into result codes of the format [{]\d+(, \d+)*[}]([hl]\d+)?
# where the numbers inside the braces are results of a set of rolls
# and the [hl] followed by a number indicates to keep as many highest or lowest rolls

import logging
from math import isnan, nan
from ply import lex, yacc
from signal import raise_signal, SIGABRT, signal
from random import randint as rand
import re
import threading

currentName = ""
MAX_EXECUTION_SECONDS = 2

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
	"OPEN",
	"CLOSE",
	"DIE",
]

t_PLAINTEXT = r'.+?'
t_PLUS = r'\s*\+\s*'
t_MINUS = r'\s*-\s*'
t_MULTIPLY = r'\s*\*\s*'
t_DIVIDE = r'\s*/\s*'
t_OPEN = r"\s*[{[(]\s*"
t_CLOSE = r"\s*[)\]}]\s*"


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
	log.error(f"Unable to tokenise {value} at position {t.lexpos} in {data}.")
	t.lexer.skip(1)


lexer = lex.lex(reflags=lexerRegexFlags)

precedence = (
	('left', 'expr', 'OPEN', 'CLOSE'),
	('left', 'PLUS', 'MINUS'),
	('left', 'MULTIPLY', 'DIVIDE'),
	('left', 'brackets', 'UNARY'),
	('left', 'DIE', 'NUMBER'),
)


def p_expr2exprexpr(p):
	'expr : expr expr %prec expr'
	log.debug("Parsing expr concatination " + str(p[1:]))
	p[0] = p[1] + p[2]


def p_expr2PLAINTEXT(p):
	'''expr : PLAINTEXT
	| PLUS
	| MINUS
	| MULTIPLY
	| DIVIDE
	| OPEN
	| CLOSE %prec expr
	'''
	log.debug("Parsing elevation to expr " + str(p[1:]))
	p[0] = p[1]


def p_expr2numeric(p):
	'expr : numeric %prec expr'
	log.debug("Parsing numeric to expr " + str(p[1:]))
	text = p[1]['text']
	if text.isdigit() or text == '[]':
		p[0] = text
	else:
		result = p[1]['result']
		if isnan(result):
			result = "[DIVISION BY ZERO]"
		else:
			result = f"{result:n}" if int(result) == result else f"{result:.2f}"
			while "." in result and result[-1] == "0":
				result = result[:-1]
		p[0] = f"{p[1]['text']} = {result}"


def p_numeric2PLUSMINUS(p):
	'''numeric : numeric PLUS numeric
	| numeric MINUS numeric'''
	log.debug("Parsing PLUSMINUS " + str(p[1:]))
	if '-' in p[2]:
		p[3]['result'] *= -1
	text = p[1]['text'] + p[2] + p[3]['text']
	result = p[1]['result'] + p[3]['result']
	p[0] = dict(text=text, result=result)


def p_numeric2MULTIPLY(p):
	'numeric : numeric MULTIPLY numeric'
	log.debug("Parsing multiply " + str(p[1:]))
	text = p[1]['text'] + p[2] + p[3]['text']
	result = p[1]['result'] * p[3]['result']
	p[0] = dict(text=text, result=result)


def p_numeric2DIVIDE(p):
	'numeric : numeric DIVIDE numeric'
	log.debug("Parsing divide " + str(p[1:]))
	if p[3]['result']:
		result = p[1]['result'] / p[3]['result']
	else:
		p[3]['text'] = f"~~{p[3]['text']}~~"
		result = nan
	text = p[1]['text'] + p[2] + p[3]['text']
	p[0] = dict(text=text, result=result)


def p_numeric2UNARY_PLUSMINUS(p):
	'''numeric : PLUS numeric
	| MINUS numeric %prec UNARY'''
	log.debug("Parsing unary operator " + str(p[1:]))
	text = p[1] + p[2]['text']
	result = p[2]['result']
	if '-' in p[1]:
		result *= -1
	p[0] = dict(text=text, result=result)


def p_numeric2NUMBER(p):
	'numeric : NUMBER'
	log.debug("Parsing number " + str(p[1:]))
	result = p[1]
	text = str(result)
	p[0] = dict(text=text, result=result)


def p_numeric2brackets(p):
	'numeric : OPEN numeric CLOSE %prec brackets'
	log.debug("Parsing brackets " + str(p[1:]))
	text = p[1] + p[2]['text'] + p[3]
	p[0] = dict(text=text, result=p[2]['result'])


def p_numeric2DIE(p):
	'numeric : DIE'
	log.debug("Parsing die " + str(p[1:]))
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


def randint(low, high):
	res = rand(low, high)
	log.info(f"{currentName} rolled {res}/{high}")
	return res


def p_expr2error(p):
	'expr : error'
	log.debug("Parsing error " + str(p[1:]))
	p[0] = '**<ERROR>**'


def p_error(p):
	if p:
		value = repr(p.value)
		data = repr(p.lexer.lexdata)
		log.error(f"Unable to parse the token {value} of type {p.type} at position {p.lexpos} in {data}.")
	else:
		log.error("Parser ran out of tokens to parse.")


class ParserTimeoutError(Exception):
	pass


def SIGABRT_handler(*args, **kwargs):
	raise ParserTimeoutError(f"Exceeded maximum execution time for parsing of {MAX_EXECUTION_SECONDS} seconds.")


def timedParse(*args, **kwargs):
	timer = threading.Timer(MAX_EXECUTION_SECONDS, raise_signal, args=(SIGABRT,))
	timer.start()
	try:
		return original_parser(*args, **kwargs)
	finally:
		timer.cancel()


parser = yacc.yacc()
original_parser = parser.parse
parser.parse = timedParse
signal(SIGABRT, SIGABRT_handler)
