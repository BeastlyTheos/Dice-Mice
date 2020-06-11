# Dice Mice
*seemlessly roll dice within discord chat*

:game_die::game_die::game_die:

## installation
1. visit the [authorisation page](https://discord.com/api/oauth2/authorize?client_id=719095785513418753&permissions=0&scope=bot)
2. select the server you wish to add the bot to.
3.  click authorise.
4. Your dice mice should arrive in your server shortly, ready to roll.

## Examples:
* Simply write standard RPG dice codes within your discord messages, and let the dice mice do the rest.
*
  * Theo types, "Attack the goblin for d20+5".
  * Dice Mice types, "Theo: Attack the goblin for [18]+5 = 23".
*
  * Nicole types, "Deals d8 + 3d6 +3 damage to the troll with an arrow straight in the forehead!"
  * Dice Mice types, "Nicole: Deals [6] + [3, 5, 2] +3 = 19 damage to the troll with an arrow straight in the forehead!"
*
  * Franklin types, "heals his comrade for 2d4-2 hit points."
  * Dice Mice types, "Franklin: heals his comrade for [1, 3]-2 = 2 hit points."

## syntax
dice codes have the syntax `[<num dice>]d<num sides>`.
num dice (optional) is the number of dice to roll, and must be non-negative.
num sides is the number of sides the dice should have, and must be a positive number. E.G. d6 is a six-sided die, and d12 is a 12-sided die.

## Upcoming Features
*  option to only sum up the highest/lowest dice when rolling multiple dice
*  shortcuts for rolling with advantage and disadvantage
*  user-defined macros
*  feature to repeat recent commands
*  optionally printout details about how the message was parsed to assist in debugging and learning syntax
*  syntax for repeating a set of rolls
*  evaluate multiplication and division
