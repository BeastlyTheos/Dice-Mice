# Dice Parser
# exports a yacc parser that parses dice codes from a string
# dice codes are converted into result codes of the format [{]\d+(, \d+)*[}]([hl]\d+)?
# where the numbers inside the braces are results of a set of rolls
# and the [hl] followed by a number indicates to keep as many highest or lowest rolls

from ply import lex

tokens = [
	"DIE",
	"PLAINTEXT",
]

t_PLAINTEXT = r'.'


def t_DIE(t):
	r'(?<!\w)[Dd](?P<numSides>[1-9]\d*)'
	t.value = t.lexer.lexmatch.groupdict()
	t.value['numSides'] = int(t.value['numSides'])
	return t


def t_error(t):
	print(f"Error tokenising starting at position {t.lexer.lexpos}. Remaining text is {t.value}")
	t.lexer.skip(1)


lexer = lex.lex()
