import sys
import os

class File:
    
    def __init__(self, file_name):
        with open(file_name, "r") as opened_file:
            read_file = opened_file.read()
            self.lines = read_file.split("\n")
        self.rule_nb = 0
        self.fact_nb = 0
        self.queri_nb = 0
        self.rules = []
        self.conclusions = []

    def display_lines(self):
        i = 0
        while i < len(self.lines):
            print(self.lines[i])
            i = i + 1

    def is_imply(self, line, i):
        if i + 1 < len(line) and line[i] == '=' and line[i + 1] == '>':
            return True
        elif i - 1 >= 0 and  line[i - 1] == '=' and line[i] == '>':
            return True
        else:
            return False

    def is_logical(self, c, line, i):
        if c != '(' and c != ')' and c != '!' and c != '+' and c != '|' and c != '^' and self.is_imply(line, i) == False:
            return False
        else:
            return True

    def is_operator(self, c):
        if c != '+' and c != '|' and c != '^':
            return False
        else:
            return True

    def check_if_comment(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j] == ' ' or line[j] == '\t':
                pass
            else:
                return False
            j = j + 1
        return True

    def check_rule_newline(self, line, i):
        if i == 1 and self.rule_nb == 0:
            print("line : " + line + "\t\tError format: No newline before facts when no comments.")
            return False
        elif i > 1:
            if self.lines[i - 1] != '' and self.rule_nb == 0:
                print("line : " + line + "\t\tError format: No newline before facts.")
                return False
        return True

    def rule_in_one_block(self, line, i):
        if self.rule_nb > 0 and i > 0 and self.lines[i - 1] != '':
            if self.lines[i - 1][0].isupper() == False and self.lines[i - 1][0] != '!' and self.lines[i - 1][0] != '(':
                print ("line : " + line + "\t\tError format: all facts must be in one block.")
                return False
        elif self.rule_nb > 0 and i > 0 and self.lines[i - 1] == '':
            print ("line : " + line + "\t\tError format: all facts must be in one block.")
            return False
        return True

    def rule_check_char(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j].isupper() and  j > 0 and line[j - 1].isupper():
                print(line[j-1])
                print ("line : " + line + "\t\tError format: two adjacent chars: " + line[j])
                return False
            if line[j].isupper() == False and self.is_logical(line[j], line, j) == False and line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: fact character unvalid: " + line[j])
                return False
            j = j + 1
        return True

    def rule_enough_info(self, line, i):
        j = 0
        nb_implies = 0
        a = 0
        b = 0
        while j < len(line) and line[j] != '#':
            if (line[j].isupper() and nb_implies == 0):
                a = a + 1
            if (line[j].isupper() and nb_implies == 1):
                b = b + 1
            if self.is_imply(line, j) == True:
                nb_implies = nb_implies + 1
                j = j + 1
            j = j + 1
        if a == 0:
            print ("line : " + line + "\t\tError format: No proposition before implie.")
            return False
        if  nb_implies != 1:
            if nb_implies > 1:
                print ("line : " + line + "\t\tError format: To many implies.")
            else:
                print ("line : " + line + "\t\tError format: No imply.")
            return False
        if b == 0:
            print ("line : " + line + "\t\tError format: No proposition after implie.")
            return False
        return True

    def check_parentheses(self, line, i):
        j = 0
        opened_par = 0
        closed_par = 0
        while j < len(line) and line[j] != '#':
            if line[j] == '(':
                opened_par = opened_par + 1
            elif line[j] == ')':
                closed_par = closed_par + 1
            j = j + 1
        if opened_par != closed_par:
            print ("line : " + line + "\t\tError format: Parentheses format error.")
            return False
        return True

    def check_par_content(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j] == '(':
                k = j + 1
                content = 0
                while k < len(line) and line[k] != '#' and line[k] != ')':
                    if line[k].isupper():
                        content = content + 1
                    k = k + 1
                if content == 0:
                    print ("line : " + line + "\t\tError format: Parentheses contains nothing.")
                    return False
            j = j + 1
        return True

    def check_not(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j] == '!':
                if j + 1 >= len(line):
                    print ("line : " + line + "\t\tError format: \"!\" at end of line.")
                    return False
                elif line[j + 1].isupper() == False and line[j + 1] != '(':
                    print ("line : " + line + "\t\tError format: \"!\" not followed by capital letter or parentheses.")
                    return False
            j = j + 1
        return True

    def check_around_operator(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if self.is_operator(line[j]):
                k = j - 1
                while k >= 0 and (line[k] == ' ' or line[k] == '\t'):
                    k = k - 1
                if line[k].isupper() == False and line[k] != ')':
                    print ("line : " + line + "\t\tError format: no capital letter or \")\" before operator: " + line[j])
                    return False
                k = j + 1
                while k < len(line)  and (line[k] == ' ' or line[k] == '\t'):
                    k = k + 1
                if k >= len(line) or (line[k].isupper() == False and line[k] != '(' and line[k] != '!'):
                    print ("line : " + line + "\t\tError format: no capital letter, \"!\" or \"(\" after operator: " + line[j])
                    return False
            j = j + 1
        return True

    def check_letters_in_a_row(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j].isupper():
                k = j + 1
                while k < len(line) and line[k] != '#' and (line[k] == ' ' or line[k] == '\t'):
                    k = k + 1
                if k < len(line) and (line[k].isupper() or line[k] == '!' or line[k] == '('):
                    print ("line : " + line + "\t\tError format: letter followed by letter, \"!\", or \"(\" at char: " + line[j])
                    return False
            j = j + 1
        return True

    def check_conclusion(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#' and self.is_imply(line, j) == False:
            j = j + 1
        while j < len(line) and line[j] != '#':
            if line[j] == '|' or line[j] == '^':
                print ("line : " + line + "\t\tError format: Conclusion contains undefined behaviour at char : " + line[j])
                return False
            j = j + 1
        return True

    def check_fact(self, line, i):
        if line[0] != '=':
            print ("line : " + line + "\t\tError format: fact line doesn't start with \"=\"")
            return False
        j = 1
        while j < len(line) and line[j].isupper():
            j = j + 1
        while j < len(line) and line[j] != '#':
            if line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: fact line unvalid char at : " + line[j])
                return False
            j = j + 1
        return True

    def check_queri(self, line, i):
        if line[0] != '?':
            print ("line : " + line + "\t\tError format: queri line doesn't start with \"?\"")
            return False
        j = 1
        while j < len(line) and line[j].isupper():
            j = j + 1
        while j < len(line) and line[j] != '#':
            if line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: queri line unvalid char at : " + line[j])
                return False
            j = j + 1
        return True

    def rule_is_ok(self, line, i):
        if self.check_rule_newline(line, i) == False or self.rule_in_one_block(line, i) == False:
            return False
        if self.rule_check_char(line, i) == False or self.rule_enough_info(line, i) == False:
            return False
        if self.check_parentheses(line, i) == False or self.check_par_content(line, i) == False:
            return False
        if self.check_not(line, i) == False or self.check_around_operator(line, i) == False:
            return False
        if self.check_letters_in_a_row(line, i) == False or self.check_conclusion(line, i) == False:
            return False
        self.rule_nb = self.rule_nb + 1
        return True

    def display_rules(self):
        i = 0
        while i < len(self.rules):
            print(self.rules[i])
            i = i + 1

    def add_rule(self, line):
        treat_line = line.replace(" ", "")
        treat_line_bis = treat_line.replace("\t", "")
        treat_line_ter = treat_line_bis.split("#")
        treat_line_quar = treat_line_ter[0].split("=")
        conclusion = treat_line_quar[1].replace(">", "")
        self.rules.append(treat_line_quar[0])
        self.conclusions.append(conclusion)

    def fact_is_ok(self, line, i):
        if self.fact_nb != 0:
            print("Error format: Too many fact lines")
            return False
        if self.rule_nb == 0:
            print("Error format: No rules before facts")
            return False
        if self.lines[i - 1] != '':
            print("Error format: No newline before facts")
            return False
        if self.check_fact(line, i) == False:
            return False
        else:
            self.fact_nb = self.fact_nb + 1
            return True

    def display_facts(self):
        print(self.facts)

    def add_facts(self, line):
        treat_line = line.replace(" ", "")
        treat_line_bis = treat_line.replace("\t", "")
        treat_line_ter = treat_line_bis.split("#")
        treat_line_quar = treat_line_ter[0].replace("=", "")
        self.facts = treat_line_quar

    def queri_is_ok(self, line, i):
        if self.queri_nb != 0:
            print("Error format: Too many queri lines")
            return False
        if self.rule_nb == 0:
            print("Error format: No rules before queries")
            return False
        if self.fact_nb == 0:
            print("Error format: No facts before queries")
        if self.lines[i - 1] != '':
            print("Error format: No newline before queries")
            return False
        if self.check_queri(line, i) == False:
            return False
        else:
            self.queri_nb = self.queri_nb + 1
            return True

    def display_queries(self):
        print(self.queris)

    def add_queries(self, line):
        treat_line = line.replace(" ", "")
        treat_line_bis = treat_line.replace("\t", "")
        treat_line_ter = treat_line_bis.split("#")
        treat_line_quar = treat_line_ter[0].replace("?", "")
        self.queris = treat_line_quar

    def parse(self):
        i = 0
        while i < len(self.lines):
            j = 0
            if self.lines[i] == '':
                pass
            elif self.lines[i][0] == '#':
                pass
            elif self.lines[i][0].isupper() or self.lines[i][0] == '(' or self.lines[i][0] == '!':
                if self.rule_is_ok(self.lines[i], i):
                    self.add_rule(self.lines[i])
                else:
                    print ("Error type: rule")
                    return False
            elif self.lines[i][0] == '=':
                if self.fact_is_ok(self.lines[i], i):
                    self.add_facts(self.lines[i])
                else:
                    print ("Error type: fact")
                    return False
            elif self.lines[i][0] == '?':
                if self.queri_is_ok(self.lines[i], i):
                    self.add_queries(self.lines[i])
                else:
                    print ("Error type: queri")
                    return False
            elif self.check_if_comment(self.lines[i], i) == False:
                    print ("Error type: line is not a rule, fact, queri, comment, or empty line")
                    return False
            i = i + 1
        return True

    def display_data(self):
        j = 0
        while j < len(self.rules):
            print(self.rules[j] + " => " + self.conclusions[j])
            j = j + 1
        print()
        self.display_facts()
        print()
        self.display_queries()

def treat_entry(arg):
    if os.path.isfile(arg):
        fichier = File(arg)
        if fichier.parse() and fichier.rule_nb != 0 and fichier.fact_nb == 1 and fichier.queri_nb == 1:
            fichier.display_data()
            #verify if any incoherences in rules or not -> backward chaining
            #verify if any endless reasonning in rules or not -> backward chaining
            #verify is there is any unknown statement(from rules) in fact and query -> say its undetermined
            #proceed to treatment of information
            pass
        else:
            print("File " + arg + " not well formated.")
    else:
        print ("File " + arg + " not found")

def main(argv):
    i = 0
    for arg in argv:
        if arg.find('.txt') > 0:
            treat_entry(arg)
        else:
            print ("File " + arg + " not well formated. Please give .txt files only.")
        if i != len(argv) - 1:
            print("\n-----------------------------------\n")
        i = i + 1

if __name__ == "__main__":
    main(sys.argv[1:])
