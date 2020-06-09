# Dice Parser
# exports a yacc parser that parses dice codes from a string
# dice codes are converted into result codes of the format [{]\d+(, \d+)*[}]([hl]\d+)?
# where the numbers inside the braces are results of a set of rolls
# and the [hl] followed by a number indicates to keep as many highest or lowest rolls

from ply import lex, yacc
from random import randint

tokens = [
	"DIE",
	"PLAINTEXT",
]

t_PLAINTEXT = r'.'


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


def p_expr2DIE(p):
	'expr : DIE'
	p[0] = str(randint(1, p[1]['numSides']))


def p_error(p):
	print(f"Syntax error in input at {p}")


parser = yacc.yacc()
