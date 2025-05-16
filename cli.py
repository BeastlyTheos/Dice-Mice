#! /usr/bin/python3.8
import argparse
from collections import namedtuple
import logging

from mice import handleInput

GREETING = """
I am your dice mice, ready to roll.
Just type your dice codes, and I'll echo your message back with the dice already rolled.
For more help, check out https://github.com/BeastlyTheos//Dice-Mice
Press ctrl+c at anytime to exit
"""
Author = namedtuple("author", "id display_name")
author = Author(0, "")

argparser = argparse.ArgumentParser()
argparser.add_argument(
	'-v', "--verbose",
	action='count', default=0,
	help="Increase the output verbosity. Can be used up to 3 times.",
)
args = argparser.parse_args()

logging.basicConfig(
	level=40 - 10 * args.verbose,
	format="{levelname}: {message}. In {filename}, {funcName} line {lineno}",
	datefmt="%b %d %H:%M",
	style="{",
)
log = logging.getLogger("main")

if __name__ == '__main__':
	try:
		print(GREETING)
		while True:
			print(handleInput(author, input()))
	except KeyboardInterrupt:
		print("Goodbye")
