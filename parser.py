from random import randint

from ply import lex
import ply.yacc as yacc

tokens = (
	'PLUS',
	'MINUS',
	'TIMES',
	'DIV',
	'LPAREN',
	'RPAREN',
	'NUMBER',
	'DIE',
)

t_ignore = ' \t'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIV = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_NUMBER(t):
	r'[0-9]+'
	t.value = int(t.value)
	return t


def t_DIE(t):
	r'[dD]\d+'
	t.value = int(t.value[1:])
	return t


def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)


def t_error(t):
	print("Invalid Token:", t.value[0])
	t.lexer.skip(1)


lexer = lex.lex()

precedence = (
	('left', 'PLUS', 'MINUS'),
	('left', 'TIMES', 'DIV'),
	('nonassoc', 'UMINUS'),
	('nonassoc', 'DIE'),
)


def p_add(p):
	'expr : expr PLUS expr'
	p[0] = p[1] + p[3]


def p_sub(p):
	'expr : expr MINUS expr'
	p[0] = p[1] - p[3]


def p_expr2uminus(p):
	'expr : MINUS expr %prec UMINUS'
	p[0] = - p[2]


def p_mult_div(p):
	'''expr : expr TIMES expr
		| expr DIV expr'''
	if p[2] == '*':
		p[0] = p[1] * p[3]
	else:
		if p[3] == 0:
			print("Can't divide by 0")
			raise ZeroDivisionError('integer division by 0')
		p[0] = p[1] / p[3]


def p_pDIE2DIE(p):
	'pDIE : DIE'
	p[0] = randint(1, p[1])
	print(f"set die to {p[0]}")


def p_expr2exprDIE(p):
	'expr : expr pDIE %prec DIV'
	p[0] = p[1] * p[2]


def p_expr2NUM(p):
	'''expr : pDIE
		| NUMBER'''
	p[0] = p[1]


def p_parens(p):
	'expr : LPAREN expr RPAREN'
	p[0] = p[2]


def p_error(p):
	print("Syntax error in input!")


parser = yacc.yacc()

# res = parser.parse("-4*-(3-5)")  # the input
res = parser.parse("2*-d8+d9")
print(res)

# os.remove("parser.out")
# os.remove("parsetab.py")
