from parser import Parser

class struct_fact:
    
    def __init__(self, name, index, status = "F"):
        self.name = name
        self.false_confirmed = False
        self.index = index
        self.status = status
        self.protect_contradiction = []
        self.already_checked = False
        self.is_contradictory = False
        self.dependant_rules = []
        self.rules_i_depend_on = []

class struct_rule:
    
    def __init__(self, rule, conclusion, index):
        self.rule_npi = rule
        self.conclusion = conclusion
        self.status = "U"
        self.index = index
        self.already_checked = False
        self.implies_yes = []
        self.implies_no = []
        self.depends_on = []

class Graph:
    
    def __init__(self, parser):
        self.parser = parser
        self.struct_facts = []
        self.struct_rules = []
        self.correspondance = {}

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
            print ("struct fact of " + self.struct_facts[i].name + "\n\talready checked = ", end='')
            print(self.struct_facts[i].already_checked)
            print("\tindex = ", end='')
            print (self.struct_facts[i].index)
            print ("\tstatus = " + self.struct_facts[i].status)
            print("\tis_contradictory = ",end='')
            print(self.struct_facts[i].is_contradictory)
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
        while i < len(self.parser.facts):
            if self.parser.facts[i].isupper() and self.struct_fact_doesnt_exist(self.parser.facts[i]):
                self.struct_facts.append(struct_fact(self.parser.facts[i], len(self.struct_facts), "T"))
                self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
            i += 1
        i = 0
        while i < len(self.parser.polish):
            j = 0
            while j < len(self.parser.polish[i]):
                if self.parser.polish[i][j].isupper() and self.struct_fact_doesnt_exist(self.parser.polish[i][j]):
                    self.struct_facts.append(struct_fact(self.parser.polish[i][j], len(self.struct_facts)))
                    self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
                j += 1
            i += 1
        i = 0
        while i < len(self.parser.conclusions):
            j = 0
            while j < len(self.parser.conclusions[i]):
                if self.parser.conclusions[i][j].isupper() and self.struct_fact_doesnt_exist(self.parser.conclusions[i][j]):
                    self.struct_facts.append(struct_fact(self.parser.conclusions[i][j], len(self.struct_facts)))
                    self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
                j += 1
            i += 1
        i = 0
        while i < len(self.parser.queries):
            if self.parser.queries[i].isupper() and self.struct_fact_doesnt_exist(self.parser.queries[i]):
                self.struct_facts.append(struct_fact(self.parser.queries[i], len(self.struct_facts)))
                self.correspondance[self.struct_facts[len(self.struct_facts) - 1].name] = self.struct_facts[len(self.struct_facts) - 1].index
            i += 1

    def display_rules_structures(self):
        i = 0
        while i < len(self.struct_rules):
            print ("struct rules of " + self.struct_rules[i].rule_npi + " => "+self.struct_rules[i].conclusion +  "\n\tindex = ", end='')
            print (self.struct_rules[i].index)
            print ("\talready checked = ", end='')
            print(self.struct_rules[i].already_checked)
            print ("\tstatus = ", end='')
            print(self.struct_rules[i].status)
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
        while i < len(self.parser.polish):
            self.struct_rules.append(struct_rule(self.parser.polish[i], self.parser.conclusions[i], i))
            j = 0
            while j < len(self.parser.conclusions[i]):
                if self.parser.conclusions[i][j].isupper() and j - 1 >= 0 and self.parser.conclusions[i][j - 1] != '!':
                    self.struct_rules[i].implies_yes.append(self.correspondance.get(self.parser.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.parser.conclusions[i][j])].rules_i_depend_on.append(i)
                elif self.parser.conclusions[i][j].isupper() and j - 1 == -1:
                    self.struct_rules[i].implies_yes.append(self.correspondance.get(self.parser.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.parser.conclusions[i][j])].rules_i_depend_on.append(i)
                elif self.parser.conclusions[i][j].isupper() and j - 1 >= 0 and self.parser.conclusions[i][j - 1] == '!':
                    self.struct_rules[i].implies_no.append(self.correspondance.get(self.parser.conclusions[i][j]))
                    self.struct_facts[self.correspondance.get(self.parser.conclusions[i][j])].rules_i_depend_on.append(i)
                j += 1
            j = 0
            while j < len(self.parser.polish[i]):
                if self.parser.polish[i][j].isupper() and self.link_doesnt_exist(self.parser.polish[i][j], self.struct_rules[i]):
                    self.struct_rules[i].depends_on.append(self.correspondance[self.parser.polish[i][j]])
                    self.struct_facts[self.correspondance.get(self.parser.polish[i][j])].dependant_rules.append(i)
                j += 1
            i += 1

    def display_graph(self):
        self.display_facts_structures()
        self.display_rules_structures()

    def create_global_graph(self):
        self.create_facts_structures()
        self.create_rules_structures()
