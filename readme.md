modules include:
bot code, which executes the main body of the program
DiceParser that extracts dice codes and rolls them, formatting them in roll codes with an evaluated result
EG: parsing the text "deals 2d8+4 damage" might output something like, "deals {5, 3}+4 = 12 damage".
dice codes have the format <numDice>d<numSides>[h|l]<inclusion number>
where the number of dice specifies the number of such dice to roll and sum together (default 1)
and the inclusion number specifies the number of the highest or lowest dice to include in the final sum (default all)


# plan
- lexer handles single-die rolls with no extra text
- lexer handles extra text without altering its formatting
- lexer does not try to handle dice with 0 sides
- parser parses single-die results without extra text
- parser handles extra text
- lexer rolls multiple dice at once
parser parses multiple dice at once
parser shows the sum of multi-die rolls
when dice rolls are embedded in a mathematical expression, parser evaluates the entire expression
test it is thread safe
implement in bot code
implement the inclusion number
