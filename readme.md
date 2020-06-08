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
results parser computes single-die results without extra text
results parser handles extra text
roll parser rolls multiple dice at once
results parser computes multiple dice at once
test it is thread safe
implement in bot code
