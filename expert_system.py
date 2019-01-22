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
        self.struct_facts = []
        self.struct_rules = []
        self.correspondance = {}

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

    def replace_char(self, line, char, i):
        tmp = list(line)
        tmp[i] = char
        return "".join(tmp)

    def struct_fact_doesnt_exist(self, char):
        i = 0
        while i < len(self.struct_facts):
            if char == self.struct_facts[i].name:
                return False
            i += 1
        return True

    def display_facts_structures(self):
        i = 0
        while i < len(self.struct_facts):
            print ("struct fact of " + self.struct_facts[i].name + "\n\tindex = ", end='')
            print (self.struct_facts[i].index)
            print ("\tstatus = " + self.struct_facts[i].status)
            j = 0
            print ("\trules dependant of " + self.struct_facts[i].name + ":")
            if (len(self.struct_facts[i].dependant_rules) == 0):
                print ("\t\tNone")
            while j < len(self.struct_facts[i].dependant_rules):
                print ("\t\tstruct rule index: ", end='')
                print (self.struct_facts[i].dependant_rules[j], end='')
                print (" = " + self.struct_rules[self.struct_facts[i].dependant_rules[j]].rule_npi)
                j += 1
            j = 0
            print ("\t" + self.struct_facts[i].name + " depends on those rules:")
            if (len(self.struct_facts[i].rules_i_depend_on) == 0):
                print ("\t\tNone")
            while j < len(self.struct_facts[i].rules_i_depend_on):
                print ("\t\tstruct rule index: ", end='')
                print(self.struct_facts[i].rules_i_depend_on[j], end='')
                print (" = " + self.struct_rules[self.struct_facts[i].rules_i_depend_on[j]].rule_npi)
                j += 1
            print()
            i += 1
        print (self.correspondance)

    def create_facts_structures(self):
        i = 0
        while i < len(self.facts):
            if self.facts[i].isupper() and self.struct_fact_doesnt_exist(self.facts[i]):
                self.struct_facts.append(struct_fact(self.facts[i], len(self.struct_facts), "T"))
                self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
            i += 1
        i = 0
        while i < len(self.polish):
            j = 0
            while j < len(self.polish[i]):
                if self.polish[i][j].isupper() and self.struct_fact_doesnt_exist(self.polish[i][j]):
                    self.struct_facts.append(struct_fact(self.polish[i][j], len(self.struct_facts)))
                    self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
                j += 1
            i += 1
        i = 0
        while i < len(self.conclusions):
            j = 0
            while j < len(self.conclusions[i]):
                if self.conclusions[i][j].isupper() and self.struct_fact_doesnt_exist(self.conclusions[i][j]):
                    self.struct_facts.append(struct_fact(self.conclusions[i][j], len(self.struct_facts)))
                    self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
                j += 1
            i += 1
        i = 0
        while i < len(self.queris):
            if self.queris[i].isupper() and self.struct_fact_doesnt_exist(self.queris[i]):
                self.struct_facts.append(struct_fact(self.queris[i], len(self.struct_facts)))
                self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
            i += 1

    def display_rules_structures(self):
        i = 0
        while i < len(self.struct_rules):
            print ("struct rules of " + self.struct_rules[i].rule_npi + " => "+self.struct_rules[i].conclusion +  "\n\tindex = ", end='')
            print (self.struct_facts[i].index)
            print ("\talready checked = ", end='')
            print(self.struct_rules[i].already_checked)
            j = 0
            print ("\tlist implies yes " + ":")
            if (len(self.struct_rules[i].implies_yes) == 0):
                print ("\t\tNone")
            while j < len(self.struct_rules[i].implies_yes):
                print ("\t\tstruct facts index: ", end='')
                print(self.struct_rules[i].implies_yes[j], end='')
                print (" = " + self.struct_facts[self.struct_rules[i].implies_yes[j]].name)
                j += 1
            j = 0
            print ("\tlist implies no " + ":")
            if (len(self.struct_rules[i].implies_no) == 0):
                print ("\t\tNone")
            while j < len(self.struct_rules[i].implies_no):
                print ("\t\tstruct facts index: ", end='')
                print(self.struct_rules[i].implies_no[j], end='')
                print (" = " + self.struct_facts[self.struct_rules[i].implies_no[j]].name)
                j += 1
            j = 0
            print ("\t" + self.struct_rules[i].rule_npi + " depends on those facts:")
            if (len(self.struct_rules[i].depends_on) == 0):
                print ("\t\tNone")
            while j < len(self.struct_rules[i].depends_on):
                print ("\t\tstruct fact index: ", end='')
                print (self.struct_rules[i].depends_on[j], end='')
                print (" = " + self.struct_facts[self.struct_rules[i].depends_on[j]].name)
                j += 1
            print()
            print (self.correspondance)
            i += 1

    def link_doesnt_exist(self, char, rule_struct):
        i = 0
        while i < len(rule_struct.depends_on):
            if self.struct_facts[rule_struct.depends_on[i]].name == char:
                return False
            i+= 1
        return True

    def create_rules_structures(self):
        i = 0
        while i < len(self.polish):
            self.struct_rules.append(struct_rule(self.polish[i], self.conclusions[i], i))
            j = 0
            while j < len(self.conclusions[i]):
                if self.conclusions[i][j].isupper() and j + 1< len(self.conclusions[i]) and self.conclusions[i][j + 1] != '!':
                    self.struct_rules[i].implies_yes.append(self.correspondance.get(self.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.conclusions[i][j])].rules_i_depend_on.append(i)
                elif self.conclusions[i][j].isupper() and j + 1 == len(self.conclusions[i]):
                    self.struct_rules[i].implies_yes.append(self.correspondance.get(self.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.conclusions[i][j])].rules_i_depend_on.append(i)
                elif self.conclusions[i][j].isupper() and j + 1 < len(self.conclusions[i]) and self.conclusions[i][j + 1] == '!':
                    self.struct_rules[i].implies_no.append(self.correspondance.get(self.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.conclusions[i][j])].rules_i_depend_on.append(i)
                    j += 1
                j += 1
            j = 0
            while j < len(self.polish[i]):
                if self.polish[i][j].isupper() and self.link_doesnt_exist(self.polish[i][j], self.struct_rules[i]):
                    self.struct_rules[i].depends_on.append(self.correspondance[self.polish[i][j]])
                    self.struct_facts[self.correspondance.get(self.polish[i][j])].dependant_rules.append(i)
                j += 1
            i += 1

    def create_global_graph(self):
        self.create_facts_structures()
        self.display_facts_structures()
        self.create_rules_structures()
        self.display_rules_structures()
        self.display_facts_structures()

    def solve(self):
        #reprendre ici !!!
        pass

class struct_fact:
    
    def __init__(self, name, index, status = "U"):
        self.name = name
        self.index = index
        self.status = status
        self.dependant_rules = []
        self.rules_i_depend_on = []

class struct_rule:
    
    def __init__(self, rule, conclusion, index):
        self.rule_npi = rule
        self.conclusion = conclusion
        self.index = index
        self.already_checked = False
        self.implies_yes = []
        self.implies_no = []
        self.depends_on = []

def treat_entry(arg):
    if os.path.isfile(arg):
        fichier = File(arg)
        if fichier.parse() and fichier.rule_nb != 0 and fichier.fact_nb == 1 and fichier.queri_nb == 1:
            fichier.distribute_conclusion()
            fichier.display_data()
            fichier.treat_rules()
            fichier.display_polishes()
            fichier.create_global_graph()
            fichier solve()
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
    st = "abcd"
    print(st == "abcd")
    main(sys.argv[1:])
