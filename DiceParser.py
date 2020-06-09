# Dice Parser
# exports a yacc parser that parses dice codes from a string
# dice codes are converted into result codes of the format [{]\d+(, \d+)*[}]([hl]\d+)?
# where the numbers inside the braces are results of a set of rolls
# and the [hl] followed by a number indicates to keep as many highest or lowest rolls

from ply import lex, yacc
from random import randint

tokens = [
	"DIE",
	"NUMBER",
	"PLAINTEXT",
]

t_PLAINTEXT = r'.'


def t_NUMBER(t):
	r'(?P<num>\d+(\.\d+)?)(?!\d*[Dd][1-9])'
	m = t.lexer.lexmatch
	val = m.group('num')
	try:
		t.value = int(val)
	except ValueError:
		t.value = float(val)
	return t


def t_DIE(t):
	r'(?<!\w)(?P<numDice>\d+)?[Dd](?P<numSides>[1-9]\d*)'
	t.value = t.lexer.lexmatch.groupdict()
	t.value['numDice'] = int(t.value['numDice']) if t.value['numDice'] else 1
	t.value['numSides'] = int(t.value['numSides'])
	return t


def t_error(t):
	print(f"Error tokenising starting at position {t.lexer.lexpos}. Remaining text is {t.value}")
	t.lexer.skip(1)


lexer = lex.lex()

precedence = (
	('left', 'expr'),
)


def p_expr2exprexpr(p):
	'expr : expr expr %prec expr'
	p[0] = p[1] + p[2]


def p_expr2PLAINTEXT(p):
	'''expr : PLAINTEXT'''
	p[0] = p[1]


def p_expr2numeric(p):
	'expr : numeric'
	text = p[1]['text']
	if ',' not in text:
		p[0] = str(p[1]['result'])
	else:
		p[0] = f"{p[1]['text']} = {p[1]['result']}"


def p_numeric2NUMBER(p):
	'numeric : NUMBER'
	result = p[1]
	text = str(result)
	p[0] = dict(text=text, result=result)


def p_numeric2DIE(p):
	'numeric : DIE'
	tok = p[1]
	rolls = [randint(1, tok['numSides']) for i in range(tok['numDice'])]
	result = sum(rolls)
	text = str(rolls)
	p[0] = dict(result=result, text=text)


def p_error(p):
	print(f"Syntax error in input at {p}")


parser = yacc.yacc()
