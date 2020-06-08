modules include:
bot code
parser for extracting dice codes and rolling them
parser for computing expressions, which may contain dice results
result codes should be of the format {number[, number]}[[hl]number
where the h/l /drop token is omitted if all dice are kept
where the braces are omitted if only one die is rolled
the result syntax shall also have a format for repeated rolls


# plan
roll parser handles single-die rolls with no extra text
roll parser handles extra text without altering its formatting
roll parser does not try to handle dice with 0 sides
results parser computes single-die results without extra text
results parser handles extra text
roll parser rolls multiple dice at once
results parser computes multiple dice at once
test it is thread safe
implement in bot code


				self.assertEqual(
					tok.value['numDice'], expectedValues[0],
					f"Token for {data} has {tok.value['numDice']} dice, but should have {expectedValues[0]} dice."
				)


				self.assertEqual(
					tok.value['KeepDrop'], expectedValues[2],
					f"Token for {data} indicates to {tok.value['KeepDrop']} dice, but should indicate to {expectedValues[2]} dice."
				)
				self.assertEqual(
					tok.value['numKeepDrop'], expectedValues[3],
					f"Token for {data} indicates to keep/drop {tok.value['numKeepDrop']} dice, but should indicate to keep/drop {expectedValues[3]} dice."
				)
