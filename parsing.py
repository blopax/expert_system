import sys
import os

ALLOWED_FACTS = [chr(i) for i in range(65, 91)]
BINARY_OPERATORS = ['+', '|', '^', '=>', '<=>']
OTHER_OPERATORS = ['!', '(', ')']

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


class Parser:
    def __init__(self, name):
        self.filename = name

    def file_to_lines(self):
        """
        Get file content as list of lines
        :return list: list of lines
        """
        with open(self.filename, "r") as fd:
            file_str = fd.read()
        return file_str.split("\n")

    @staticmethod
    def strip_comment(line):
        """
        Clean lines that have comments.
        :param str line: line: full line
        :return str: cleaned_line: line without comments
        """
        if "#" in line:
            line_split = line.split('#')
            line = line_split[0]

        return line.strip()

    @staticmethod
    def check_x(rule, index, x):
        """
        Check for an item x of the rule if item before and after are allowed
        Example: a fact cannot have a fact next to it. (Somehting like AB + C => D)
        :param list rule: rule as a list of atoms (facts, operators)
        :param int index: index of the item being checked
        :param chr x: item
        :return: None
        """
        try:
            if x in ALLOWED_FACTS:
                forbid_before = ALLOWED_FACTS + [')']
                forbid_after = ALLOWED_FACTS + ['(', '!']
            elif x in BINARY_OPERATORS:
                forbid_before = BINARY_OPERATORS + ['(', '!']
                forbid_after = BINARY_OPERATORS + [')']
            elif x == ')':
                forbid_before = BINARY_OPERATORS + ['!']
                forbid_after = ALLOWED_FACTS + ['!', '(']
            else:  # ! and ( already treated above
                forbid_before, forbid_after = [], []
            if index > 0 and rule[index - 1] in forbid_before:
                raise Exception(RULE_SYNTAX.format(''.join(rule), index, x))
            if index + 1 < len(rule) and rule[index + 1] in forbid_after:
                raise Exception(RULE_SYNTAX.format(''.join(rule), index, x))
        except Exception:
            raise

    def check_error_rule(self, rule):
        """
        Check if given rule has the right format
        :param list rule: rule as a list of atoms (facts, operators)
        :return bool: True if there is an error
        """
        try:
            if rule[0] in BINARY_OPERATORS + [')']:
                raise Exception(RULE_SYNTAX.format(''.join(rule), 0, rule[0]))
            if rule[-1] in BINARY_OPERATORS + ['(', '!']:
                raise Exception(RULE_SYNTAX.format(''.join(rule), len(rule) - 1, rule[-1]))
            open_par = 0
            for i, x in enumerate(rule):
                if x == '(':
                    open_par += 1
                if x == ')':
                    open_par -= 1
                self.check_x(rule, i, x)
                if open_par < 0:
                    raise Exception(RULE_SYNTAX_PARENTHESIS.format(''.join(rule)))
            if open_par != 0:
                raise Exception(RULE_SYNTAX_PARENTHESIS.format(''.join(rule)))
            return False
        except Exception:
            raise

    def check_rules(self, rule_lines):
        """
        Check if all the rules have the right format
        :param list rule_lines: list of rule_lines, each item being a string
        :return list: list of rules, each rule being a list of atom
        """
        try:
            rules = []
            for rule_line in rule_lines:
                rule_line = rule_line.replace("\t", "").replace(" ", "")
                unauthorized_char = set(rule_line) - (set(ALLOWED_FACTS) | set(BINARY_OPERATORS) |
                                                      set(OTHER_OPERATORS) | {'<', '=', '>'})
                if unauthorized_char:
                    raise Exception(RULE_SYNTAX_UNAUTHORIZED_CHAR.format(unauthorized_char, rule_line))
                rule_line = rule_line.replace("<=>", "~").replace("=>", "-")
                rule = list(rule_line)
                rule = ["<=>" if x == "~" else x for x in rule]
                rule = ["=>" if x == "-" else x for x in rule]
                if rule:
                    self.check_error_rule(rule)
                    rules.append(rule)
            return rules
        except Exception:
            raise

    @staticmethod
    def check_facts_queries(lines, fact_or_query):
        """
        Check if facts are correct.
        :param list lines: List of strings
        :param str fact_or_query: Either 'facts' or 'queries'. Is used for error message.
        :return list: list of facts
        """
        try:
            if len(lines) != 1:
                raise Exception('All facts should be on one line, same for queries')
            char_list = list(lines[0])
            char_list.pop(0)
            if len(char_list) != len(set(char_list)):
                raise Exception(FACT_QUERY_SYNTAX_DOUBLE.format(fact_or_query, lines[0]))
            unauthorized_char = set(char_list) - set(ALLOWED_FACTS)
            if unauthorized_char:
                raise Exception(FACT_QUERY_SYNTAX_UNAUTHORIZED_CHAR.format(fact_or_query, lines[0], unauthorized_char))
            return char_list
        except Exception:
            raise

    def get_rules_facts_queries(self):
        """
        Check if queries are correct.
        :return list: list of queries
        """
        try:
            lines = self.file_to_lines()
            rule_lines, fact_lines, query_lines = [], [], []
            block = 0
            for line in lines:
                if "=>" in line and block <= 1:
                    rule_lines.append(self.strip_comment(line))
                    block = 1
                elif line.startswith("=") and block == 1:
                    fact_lines.append(self.strip_comment(line))
                    block = 2
                elif line.startswith("?") and block == 2:
                    query_lines.append(self.strip_comment(line))
                    block = 3
                elif line.startswith("#") or not line:
                    pass
                else:
                    raise Exception(FILE_SYNTAX)
            return rule_lines, fact_lines, query_lines
        except Exception:
            raise

    def parse_file(self):
        """
        Parse the file and return rules, facts, queries
        :return: rules, facts, queries
        """
        try:
            filename = self.filename
            if filename.split('.')[-1] != "txt" or not os.path.isfile(filename) or os.path.isdir(filename):
                raise Exception(FILE_INPUT_ERROR)
            rule_lines, fact_lines, query_lines = self.get_rules_facts_queries()
            rules = self.check_rules(rule_lines)
            facts = self.check_facts_queries(fact_lines, "facts")
            queries = self.check_facts_queries(query_lines, "queries")
            return rules, facts, queries
        except Exception as err:
            print(err)
            return [], [], []


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise Exception(INPUT_ERROR)
        file = sys.argv[1]
        parse = Parser(file)
        rules_lst, facts_lst, queries_lst = parse.parse_file()
        print(rules_lst, "\n", facts_lst, "\n", queries_lst)
    except Exception as e:
        print(e)
