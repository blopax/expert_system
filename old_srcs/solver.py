class Solver:
    
    def __init__(self, parser, graph):
        self.parser = parser
        self.graph = graph
        self.lst = []
        self.lst_bis = []
        self.lst_error = []
        self.lst_display = []
        self.lst_force_u = []


    def lst_error_ok(self, char):
        i = 0
        while i < len(self.lst_error):
            if self.lst_error[i] == char:
                return False
            i += 1
        return True

    def lst_force_u_ok(self, char):
        i = 0
        while i < len(self.lst_force_u):
            if char == self.lst_force_u[i]:
                return False
            i += 1
        return True

    def check_protect_contra(self, fact, char):
        i = 0
        while i < len(fact.protect_contradiction):
            if fact.protect_contradiction[i] == char:
                return True
            i += 1
        return False


    def check_is_implied(self, char, contra):
        i = 0
        if self.check_protect_contra(self.graph.struct_facts[self.graph.correspondance.get(char)], contra):
            return False
        self.graph.struct_facts[self.graph.correspondance.get(char)].protect_contradiction.append(contra)
        while i < len(self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on):
            if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].already_checked == False:
                self.solve_rule(self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]])
                if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].status == True:
                    return False
            else:
                if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].status == True or self.graph.struct_facts[self.graph.correspondance.get(char)].status != "U":
                    return False
            i += 1
        return True
    
    def force_u_rules(self, char):
        i = 0
        if self.lst_force_u_ok(char):
            self.lst_force_u.append(char)
            while i < len(self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules):
                self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].status = "U"
                self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].already_checked = False
                j = 0
                while j < len(self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes):
                    if self.check_is_implied(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes[j]].name, char):
                        self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes[j]].status = "U"
                        self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes[j]].already_checked = False
                        self.force_u_rules(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes[j]].name)
                        self.solve_query(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_yes[j]].name)
                    j += 1
                j = 0
                while j < len(self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no):
                    if self.check_is_implied(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no[j]].name, char):
                        self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no[j]].status = "U"
                        self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no[j]].already_checked = False
                        self.force_u_rules(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no[j]].name)
                        self.solve_query(self.graph.struct_facts[self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].implies_no[j]].name)
                    j += 1
                i += 1

    def set_fact_status(self, struct_fact, struct_rule):
        #returns -1 if fact.status is contradictory
        #returns 1 if fact.status well updated
        j = 0
        while j < len(self.graph.struct_rules[struct_rule.index].implies_yes):
            char = self.graph.struct_facts[self.graph.struct_rules[struct_rule.index].implies_yes[j]]
            if char.status == False and char.false_confirmed == True:
                if char.name == struct_fact.name:
                    return -1
            else:
                if char.is_contradictory == False:
                    char.status = "T"
                if self.solve_query(char.name) == False:
                    char.status = "U"
                    if self.lst_error_ok(char.name):
                        self.lst_error.append(char.name)
                        print("Error contradiction for query: " + char.name)
                        char.is_contradictory = True
                        char.status = "U"
                        self.force_u_rules(char.name)
                    if char.name == struct_fact.name:
                        return -1
                    self.set_checked_status_at_false(char.name)
                    self.set_checked_facts_at_false(char.name)
            j += 1
        j = 0
        while j < len(self.graph.struct_rules[struct_rule.index].implies_no):
            char = self.graph.struct_facts[self.graph.struct_rules[struct_rule.index].implies_no[j]]
            if char.status == True:
                if char.name == struct_fact.name:
                    return -1
            else:
                if char.is_contradictory == False:
                    char.status = "F"
                if self.solve_query(char.name) == False:
                    char.status = "U"
                    if self.lst_error_ok(char.name):
                        self.lst_error.append(char.name)
                        print("Error contradiction for query: " + char.name)
                        char.is_contradictory = True
                        char.status = "U"
                        self.force_u_rules(char.name)
                    if char.name == struct_fact.name:
                        return -1
                    self.set_checked_status_at_false(char.name)
                    self.set_checked_facts_at_false(char.name)
            j += 1
        return 1

    def lst_ok(self, char):
        i = 0
        while i < len(self.lst):
            if char == self.lst[i]:
                return False
            i += 1
        return True

    def traduce_fact(self, tmp, i):
        #print("\n\trule = " + ''.join(tmp), end='')
        if self.graph.struct_facts[self.graph.correspondance.get(tmp[i])].status != "U":
            tmp[i] = self.graph.struct_facts[self.graph.correspondance.get(tmp[i])].status
        elif self.graph.struct_facts[self.graph.correspondance.get(tmp[i])].already_checked == False and self.lst_ok(tmp[i]):
            self.solve_query(tmp[i])
            tmp[i] = self.graph.struct_facts[self.graph.correspondance.get(tmp[i])].status
        #print(" ===> " + ''.join(tmp))

    def solve_neg(self, tmp, i):
        #print("\n\trule = " + ''.join(tmp), end='')
        if tmp[i - 1] == "F":
            tmp.pop(i - 1)
            tmp.insert(i - 1, "T")
        elif tmp[i - 1] == "T":
            tmp.pop(i - 1)
            tmp.insert(i - 1, "F")
        del(tmp[i])
        #print(" ===> " + ''.join(tmp))

    def solve_and(self, tmp, i):
        char1 = tmp[i - 2]
        char2 = tmp[i - 1]
        #print("\n\trule = " + ''.join(tmp), end='')
        if char1 == "T" and char2 == "T":
            tmp.pop(i - 1)
        elif char1 == "F" or char2 == "F":
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "F")
        else:
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "U")
        del(tmp[i - 1])
        #print(" ===> " + ''.join(tmp))

    def solve_or(self, tmp, i):
        char1 = tmp[i - 2]
        char2 = tmp[i - 1]
        #print("\n\trule = " + ''.join(tmp), end='')
        if char1 == "T" or char2 == "T":
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "T")
        elif char1 == "F" and char2 == "F":
            tmp.pop(i - 1)
        else:
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "U")
        del(tmp[i - 1])
        #print(" ===> " + ''.join(tmp))

    def solve_xor(self, tmp, i):
        char1 = tmp[i - 2]
        char2 = tmp[i - 1]
        #print("\n\trule = " + ''.join(tmp), end='')
        if (char1 == "T" and char2 == "F") or (char1 == "F" and char2 == "T"):
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "T")
        elif (char1 == "T" and char2 == "T") or (char1 == "F" and char2 == "F"):
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "F")
        else:
            tmp.pop(i - 2)
            tmp.pop(i - 2)
            tmp.insert(i - 2, "U")
        del(tmp[i - 1])
        #print(" ===> " + ''.join(tmp))

    def list_bis_ok(self, index):
        i = 0
        while i < len(self.lst_bis):
            if self.lst_bis[i] == index:
                return False
            i += 1
        return True

    def solve_rule(self, rule):
        #returns -1 if rule is True
        #return -2 if rule is False
        #return 0 if unknown
        i = 0
        if self.list_bis_ok(rule.index):
            self.lst_bis.append(rule.index)
        tmp = list(rule.rule_npi)
        while i < len(tmp):
            if tmp[i].isupper():
                self.traduce_fact(tmp, i)
            i += 1
        #print("rule: " + self.graph.struct_rules[rule.index].rule_npi + " ==> " + ''.join(tmp), end='')
        i = 0
        shortened = 0
        while i < len(tmp):
            if tmp[i] == "!":
                self.solve_neg(tmp, i)
                shortened = 1
            elif tmp[i] == "+":
                self.solve_and(tmp, i)
                shortened = 1
            elif tmp[i] == "|":
                self.solve_or(tmp, i)
                shortened = 1
            elif tmp[i] == "^":
                self.solve_xor(tmp, i)
                shortened = 1
            if shortened == 0:
                i += 1
            else:
                shortened = 0
                i = 0
        if len(tmp) != 1:
            while True:
                print("ERROR rule not well analysed")
        elif rule.index in self.lst_bis:
            self.lst_bis.remove(rule.index)
        if len(tmp) == 1 and tmp[0] == "T":
            self.graph.struct_rules[rule.index].status = "T"
            self.graph.struct_rules[rule.index].already_checked = True
            #print(" ==> " + ''.join(tmp))
            return -1
        if len(tmp) == 1 and tmp[0] == "F":
            self.graph.struct_rules[rule.index].status = "F"
            self.graph.struct_rules[rule.index].already_checked = True
            #print(" ==> " + ''.join(tmp))
            return -2
        if len(tmp) == 1 and tmp[0] == "U":
            self.graph.struct_rules[rule.index].status = "U"
            self.graph.struct_rules[rule.index].already_checked = True
            #print(" ==> " + ''.join(tmp))
            return 0

    def set_checked_status_at_false(self, char):
        i = 0
        while i < len(self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules):
            if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].status == "U":
                self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].dependant_rules[i]].already_checked = False
            i += 1
        i = 0
        while i < len(self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on):
            if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].status == "U":
                self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].already_checked = False
            i += 1

    def set_checked_facts_at_false(self, char):
        i = 0
        while i < len(self.graph.struct_facts):
            if self.graph.struct_facts[i].status == "U" and self.graph.struct_facts[i].is_contradictory == False:
                self.graph.struct_facts[i].already_checked = False
            i += 1

    def rules_i_depend_on_are_checked(self, char):
        i = 0
        while i < len(self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on):
            if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(char)].rules_i_depend_on[i]].already_checked == False:
                return False
            i += 1
        return True

    def solve_query(self, char):
        if self.lst_ok(char):
            self.lst.append(char)
        fact = self.graph.struct_facts[self.graph.correspondance.get(char)]
        while self.rules_i_depend_on_are_checked(char) == False:
            j = 0
            while j < len(fact.rules_i_depend_on):
                rule = fact.rules_i_depend_on[j]
                #print("Solving rule: " + self.graph.struct_rules[rule].rule_npi)
                if self.list_bis_ok(self.graph.struct_rules[rule].index) and self.graph.struct_rules[rule].already_checked == False:
                    result = self.solve_rule(self.graph.struct_rules[rule])
                    self.graph.struct_rules[rule].already_checked = True
                else:
                    result = 0
                if result == -1: #when rule is true
                    if self.set_fact_status(fact, self.graph.struct_rules[rule]) < 0: #when contradiction
                        fact.already_checked = True
                        return False
                    else: #when no contradcition
                        self.set_checked_status_at_false(char)
                        self.set_checked_facts_at_false(char)
                        j += 1
                else:
                    j += 1
        if self.lst_ok(char) == False:
            self.lst.remove(char)
        fact.already_checked = True
        return True

    def all_queries_are_checked(self):
        i = 0
        while i < len(self.parser.queries):
            if self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].already_checked == False:
                return False
            j = 0
            while j < len(self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].rules_i_depend_on):
                if self.graph.struct_rules[self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].rules_i_depend_on[j]].already_checked == False:
                    return False
                j += 1
            i += 1
        return True

    def lst_display_ok(self, char):
        i = 0
        while i < len(self.lst_display):
            if char == self.lst_display[i]:
                return False
            i += 1
        return True

    def solve(self):
        while self.all_queries_are_checked() == False:
            i = 0
            #print(self.queries[i])
            while i < len(self.parser.queries):
                if self.solve_query(self.parser.queries[i]) == False:
                    if self.lst_error_ok(self.parser.queries[i]):
                        self.lst_error.append(self.parser.queries[i])
                        self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].is_contradictory = True
                        self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].status = "U"
                        print("Error contradiction for query: " + self.parser.queries[i])
                        self.set_checked_status_at_false(self.parser.queries[i])
                        self.set_checked_facts_at_false(self.parser.queries[i])
                        self.force_u_rules(self.parser.queries[i])
                i += 1


