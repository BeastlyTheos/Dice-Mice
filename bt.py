#!/usr/bin/python3
import argparse
import logging
import re
from sys import stdout

from DiceParser import parser, lexerRegexFlags, t_DIE, lexer  # noqa
diceRegex = re.compile(t_DIE.__doc__, flags=lexerRegexFlags)

argparser = argparse.ArgumentParser()
argparser.add_argument(
	'-v', "--verbose",
	action='count', default=0,
	help="Increase the output verbosity. Can be used up to 3 times.",
)
args = argparser.parse_args()

logging.basicConfig(
	level=40 - 10 * args.verbose,
	filename="log.log",
	format="{levelname} from {name}. {message} on {asctime}. In {filename}, {funcName} line {lineno}",
	datefmt="%b %d %H:%M",
	style="{",
)
log = logging.getLogger("main")
log.addHandler(logging.StreamHandler(stdout))

i = input()
while i:  # noqa
	print(parser.parse(i))
	i = input()

lexer.input('(8-3 ) / 2')
while tok := lexer.token():
	print(tok)
