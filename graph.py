import sys

import parser
# import node
import node_utils
import solver
import utils
# import graph


class Fact:
    def __init__(self, content):
        self.content = content
        self.value = False
        self.confirmed = False

    # contradiction si self confirmed and self value differnt of value inferred
    # ambiguity if query self.confirmed = False and Fact in Clause where fact positive
    # self.value confirmed if Fact not in any rules_conclusion


class Clause:
    def __init__(self, positive_facts=None, negative_facts=None, node=None, confirmed=False):
        self.positive_facts = set()
        self.negative_facts = set()
        self.confirmed = confirmed  # permet de voir si confirme ou pas
        self.value = False  # permet de voir si confirme ou pas

        if positive_facts:
            self.positive_facts = positive_facts
        if negative_facts:
            self.negative_facts = negative_facts

        if node:
            self.make_clause(node)
        self.is_literal = (len(self.positive_facts) + len(self.negative_facts) == 1)

    def update_clause_attributes(self, confirmed_clauses):
        if self.confirmed is True:
            return
        facts_of_clause = self.positive_facts | self.negative_facts
        for confirmed_clause in confirmed_clauses:
            if (confirmed_clause.positive_facts.issubset(self.positive_facts)
                    and confirmed_clause.negative_facts.issubset(self.negative_facts)):
                self.value = True
                self.confirmed = True
                break
            if (confirmed_clause.is_literal is True
                    and confirmed_clause.positive_facts.issubset(self.negative_facts)
                    and confirmed_clause.negative_facts.issubset(self.positive_facts)):
                facts_of_clause -= confirmed_clause.positive_facts | confirmed_clause.negative_facts
        if len(facts_of_clause) == 0:
            self.value = False
            self.confirmed = True

    def add_literal_to_clause(self, node):
        if node.content in parser.ALLOWED_FACTS:
            self.positive_facts |= {node.content}
        elif node.content == '!':
            self.negative_facts |= {node.children[0].content}

    def make_clause(self, node):
        if node.content in ['!'] + parser.ALLOWED_FACTS:
            self.add_literal_to_clause(node)
        if node.content == '|':
            for child in node.children:
                self.add_literal_to_clause(child)

    def check_horn_clauses(self):
        if len(self.positive_facts) > 1:
            return False
        return True

        # remarque is on a clause A | B savoir que B est vrai ne leve pas ambiguite sur A par contre savoir non B oui


class Rule:
    def __init__(self, body_content, head_content):
        self.premise_content = body_content  # list
        self.conclusion_content = head_content  # list
        self.fact_in_premise = set(body_content) & set(parser.ALLOWED_FACTS)  # list de char
        self.fact_in_conclusion = set(head_content) & set(
            parser.ALLOWED_FACTS)  # idem (pas besoin des facts on se sert de fonction get fact

        # fire below only if in backwards inference it is used and used_rule False
        self.premise_clauses = self.fill_clauses_from_content(self.premise_content)
        self.conclusion_clauses = self.fill_clauses_from_content(self.conclusion_content, confirmed=True)
        self.used_rule = False
        self.clauses_in_premise_all_confirmed = False  # a voir
        self.triggered = -1

    @staticmethod
    def fill_clauses_from_content(content, confirmed=False):
        node = node_utils.Node(list_input=content)
        node.transform_graph_and_or(node)
        node.transform_graph_cnf(node)
        node.flatten_graph_cnf()
        return solver.add_clause(node, confirmed=confirmed)


class Graph:
    def __init__(self, rules_lst, facts_lst, queries_lst):
        self.facts_set = set()  # Facts
        self.rules_set = set()  # Rules
        self.inferred_clauses = set()  # ??

        for rule_content in rules_lst:
            symbol, index = node_utils.find_symbol_to_treat(rule_content)
            if symbol == "=>":
                self.rules_set.add(Rule(rule_content[:index], rule_content[index + 1:]))
            elif symbol == "<=>":
                self.rules_set.add(Rule(rule_content[:index], rule_content[index + 1:]))
                self.rules_set.add(Rule(rule_content[index + 1:], rule_content[:index]))
            else:
                pass
                # mettre message erreur pour regler si pas d implication ??

        self.facts_in_rules_conclusions = set()
        for rule in self.rules_set:
            self.facts_in_rules_conclusions.update(rule.fact_in_conclusion)

        fact_content_set = set()
        for rule in self.rules_set:
            fact_content_set.update(rule.fact_in_premise)
            fact_content_set.update(rule.fact_in_conclusion)
        fact_content_set.update(set(facts_lst))
        fact_content_set.update(set(queries_lst))

        for content in fact_content_set:
            self.facts_set.add(Fact(content))
        self.set_initial_facts(facts_lst, fact_content_set)

    def get_fact(self, fact_content):
        fact = None
        for item in self.facts_set:
            if item.content == fact_content:
                fact = item
        return fact

    def set_initial_facts(self, initial_facts, fact_content_set):
        for initial_fact in initial_facts:
            fact = self.get_fact(initial_fact)
            fact.value = True
            fact.confirmed = True
        facts_in_conclusions = set()
        for rule in self.rules_set:
            facts_in_conclusions.update(rule.fact_in_conclusion)
        facts_not_in_conclusions = fact_content_set.difference(facts_in_conclusions)
        for fact_not_in_conclusions in facts_not_in_conclusions:
            fact = self.get_fact(fact_not_in_conclusions)
            fact.confirmed = True

    def get_confirmed_facts(self):
        confirmed_facts = set()
        for fact in self.facts_set:
            if fact.confirmed is True:
                confirmed_facts.add(fact.content)
        return confirmed_facts

    # initialiser inferred_clauses ac facts qui sont true ?


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise Exception(utils.INPUT_ERROR)
        file = sys.argv[1]
        parse = parser.Parser(file)
        rules_list, facts_list, queries_list = parse.parse_file()
        G = Graph(rules_list, facts_list, queries_list)

        # print(G.rules_set)
        # print(G.facts_set)
        # print(G.inferred_clauses)

    except Exception as e:
        print(e)
