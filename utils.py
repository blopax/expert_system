
RULE_SYNTAX = "Rule syntax error in rule '{}'\nat symbol position {}: '{}'"

RULE_SYNTAX_PARENTHESIS = "Rule syntax error with parenthesis in rule '{}'"

RULE_SYNTAX_UNAUTHORIZED_CHAR = "Rule syntax error: unauthorized character: {}\nin rule: '{}'"

FACT_QUERY_SYNTAX = 'All {} should be on one single line.'

FACT_QUERY_SYNTAX_DOUBLE = "Some {} appear twice in '{}'"

FACT_QUERY_SYNTAX_UNAUTHORIZED_CHAR = "Some {} are not allowed in '{}':\n{}"

FILE_SYNTAX = """File syntax error:
File should contain first rules with '=>' or '<=>', then facts starting with '=' and finally queries starting with '?'.
Nothing else but comments is accepted.)"""

FILE_INPUT_ERROR = "File input error: please provide a .txt file."

INPUT_ERROR = "Please provide only one parameter: the filename."

# Next time try dictionary for test purpose.
