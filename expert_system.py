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
        self.polish = []
        self.conclusions = []
        self.queris_status = {}
        self.facts_status = {}

    def display_lines(self):
        i = 0
        while i < len(self.lines):
            print(self.lines[i])
            i += 1

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
            j += 1
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
            j += 1
        return True

    def rule_enough_info(self, line, i):
        j = 0
        nb_implies = 0
        a = 0
        b = 0
        while j < len(line) and line[j] != '#':
            if (line[j].isupper() and nb_implies == 0):
                a += 1
            if (line[j].isupper() and nb_implies == 1):
                b += 1
            if self.is_imply(line, j) == True:
                nb_implies += 1
                j += 1
            j += 1
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
            j += 1
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
                    k += 1
                if content == 0:
                    print ("line : " + line + "\t\tError format: Parentheses contains nothing.")
                    return False
            j += 1
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
            j += 1
        return True

    def check_around_operator(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if self.is_operator(line[j]):
                k = j - 1
                while k >= 0 and (line[k] == ' ' or line[k] == '\t'):
                    k -= 1
                if line[k].isupper() == False and line[k] != ')':
                    print ("line : " + line + "\t\tError format: no capital letter or \")\" before operator: " + line[j])
                    return False
                k = j + 1
                while k < len(line)  and (line[k] == ' ' or line[k] == '\t'):
                    k += 1
                if k >= len(line) or (line[k].isupper() == False and line[k] != '(' and line[k] != '!'):
                    print ("line : " + line + "\t\tError format: no capital letter, \"!\" or \"(\" after operator: " + line[j])
                    return False
            j += 1
        return True

    def check_letters_in_a_row(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j].isupper():
                k = j + 1
                while k < len(line) and line[k] != '#' and (line[k] == ' ' or line[k] == '\t'):
                    k += 1
                if k < len(line) and (line[k].isupper() or line[k] == '!' or line[k] == '('):
                    print ("line : " + line + "\t\tError format: letter followed by letter, \"!\", or \"(\" at char: " + line[j])
                    return False
            j += 1
        return True

    def check_conclusion(self, line, i):
        j = 0
        while j < len(line) and line[j] != '#' and self.is_imply(line, j) == False:
            j += 1
        while j < len(line) and line[j] != '#':
            if line[j].isupper():
                if line.rfind(line[j]) > j:
                    print ("line : " + line + "\t\tError format: Conclusion contains char : " + line[j] + ", twice.")
                    return False
            if line[j] == '|' or line[j] == '^':
                print ("line : " + line + "\t\tError format: Conclusion contains undefined behaviour at char : " + line[j])
                return False
            j += 1
        return True

    def check_fact(self, line, i):
        if line[0] != '=':
            print ("line : " + line + "\t\tError format: fact line doesn't start with \"=\"")
            return False
        j = 1
        while j < len(line) and line[j].isupper():
            j += 1
        while j < len(line) and line[j] != '#':
            if line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: fact line unvalid char at : " + line[j])
                return False
            j += 1
        return True

    def check_queri(self, line, i):
        if line[0] != '?':
            print ("line : " + line + "\t\tError format: queri line doesn't start with \"?\"")
            return False
        j = 1
        while j < len(line) and line[j].isupper():
            j += 1
        while j < len(line) and line[j] != '#':
            if line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: queri line unvalid char at : " + line[j])
                return False
            j += 1
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
        self.rule_nb += 1
        return True

    def display_rules(self):
        i = 0
        while i < len(self.rules):
            print(self.rules[i])
            i += 1

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
            i += 1
        return True

    def display_data(self):
        j = 0
        while j < len(self.rules):
            print(self.rules[j] + " => " + self.conclusions[j])
            j += 1
        print()
        self.display_facts()
        print()
        self.display_queries()

    def add_char(self, line, char, position):
        tmp = line
        tmp_bis = list(tmp)
        tmp_bis.insert(position, char)
        return ''.join(tmp_bis)

    def remove_char(self, line, position):
        tmp = line
        tmp_bis = list(tmp)
        del(tmp_bis[position])
        return ''.join(tmp_bis)

    def remove_double_neg(self, line):
        tmp = line
        j = 0
        while j < len(tmp):
            if tmp[j] == '!' and tmp[j + 1] == '!':
                tmp = self.remove_char(tmp, j)
                tmp = self.remove_char(tmp, j)
            j += 1
        return tmp

    def distribute_conclusion(self):
        i = 0
        while i < len(self.conclusions):
            j = 0
            self.conclusions[i] = self.conclusions[i].replace("+", "")
            while j < len(self.conclusions[i]):
                if self.conclusions[i][j] == '!' and self.conclusions[i][j + 1] == '(':
                    k = j + 2
                    count = 1
                    while k < len(self.conclusions[i]) and count > 0:
                        if self.conclusions[i][k] == ')':
                            count -= 1
                        elif self.conclusions[i][k] == '(':
                            count += 1
                        elif self.conclusions[i][k].isupper():
                            self.conclusions[i] = self.add_char(self.conclusions[i], '!', k)
                            k = k + 1
                        k += 1
                    self.conclusions[i] = self.remove_char(self.conclusions[i], j)
                    self.conclusions[i] = self.remove_double_neg(self.conclusions[i])
                j += 1
            self.conclusions[i] = self.conclusions[i].replace("(", "")
            self.conclusions[i] = self.conclusions[i].replace(")", "")
            i += 1

    def is_symbol(self, char):
        if char == '(' or char == ')':
            return 1
        elif char == '^':
            return 2
        elif char == '|':
            return 3
        elif char == '+':
            return 4
        elif char == '!':
            return 5
        else:
            return -1

    def reverse_polish_notation(self, line):
        i = 0
        final_str = []
        stack = []
        while i < len(line):
            if line[i].isupper():
                final_str.append(line[i])
            elif self.is_symbol(line[i]) > 0:
                if line[i] == '(':
                    stack.append(line[i])
                elif line[i] == ')':
                    k = len(stack) - 1
                    while stack[k] != '(':
                        final_str.append(stack.pop())
                        k -= 1
                    stack.pop()
                else:
                    if len(stack) > 0 and self.is_symbol(line[i]) > self.is_symbol(stack[len(stack) - 1]):
                        stack.append(line[i])
                    else:
                        j = len(stack) - 1
                        while j > 0 and self.is_symbol(line[i]) <= self.is_symbol(stack[j]):
                            final_str.append(stack.pop())
                            j -= 1
                        stack.append(line[i])
            i += 1
        i = len(stack) - 1
        while i >= 0:
            final_str.append(stack.pop())
            i -= 1
        return ''.join(final_str)

    def treat_rules(self):
        i = 0
        while i < len(self.rules):
            self.polish.append(self.reverse_polish_notation(self.rules[i]))
            i += 1

    def display_polishes(self):
        i = 0
        print()
        while i < len(self.polish):
            print(self.polish[i])
            i += 1
        print()

    def treat_facts(self):
    #use char in self.facts_status (renvoie True ou False)
        i = 0
        while i < len(self.facts):
            if self.facts[i].isupper():
                self.facts_status[self.facts[i]] = "T"
            i += 1

    def treat_queris(self):
    #T --> True
    #F --> False
    #U --> Unknown
        i = 0
        while i < len(self.queris):
            if self.queris[i].isupper():
                if self.queris[i] in self.facts_status:
                    self.queris_status[self.queris[i]] = "T"
                else:
                    self.queris_status[self.queris[i]] = "U"
            i += 1

    def replace_char(self, line, char, i):
        tmp = list(line)
        tmp[i] = char
        return "".join(tmp)

    def is_rule_true(self, line):
        print(line)
        i = 0
        tmp = line
        while i < len(tmp):
            if tmp[i].isupper():
                if tmp[i] in self.facts_status:
                    tmp = self.replace_char(tmp, 'T', i)
                else:
                    tmp = self.replace_char(tmp, 'F', i)
            elif:
                #continue HERRE avec dispatch des operators
                pass
            i += 1
        return True

    def find_solution(self):
        i = 0
        while i < len(self.queris):
            j = 0
            while j < len(self.conclusions):
                if self.conclusions[j].find(self.queris[i]) >= 0:
                    if self.is_rule_true(self.polish[j]):
                        print ("YAAAAY")
                j += 1
            i += 1

def treat_entry(arg):
    if os.path.isfile(arg):
        fichier = File(arg)
        if fichier.parse() and fichier.rule_nb != 0 and fichier.fact_nb == 1 and fichier.queri_nb == 1:
            fichier.distribute_conclusion()
            fichier.display_data()
            fichier.treat_rules()
            fichier.treat_facts()
            fichier.treat_queris()
            fichier.display_polishes()
            fichier.find_solution()
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
        i += 1

if __name__ == "__main__":
    main(sys.argv[1:])
