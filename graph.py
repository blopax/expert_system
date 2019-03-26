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
    def __init__(self):
        self.positive_facts = set()
        self.negative_facts = set()
        self.is_literal = False

        # ajouter if clause is literal (id est only one positive fact exclusive or negative fact
        # remarque is on a clause A | B savoir que B est vrai ne leve pas ambiguite sur A par contre savoir non B oui

    # creer methode qui transforme node en set de clauses (pas ds cette classe)
    # dans set on utilise les facts ou les lettre ? "A, B...") --> si graphe get_fact peut etre lettres plus leger ?


class Rule:
    def __init__(self, body_content, head_content):
        self.premise_content = body_content  # list
        self.conclusion_content = head_content  # list
        self.fact_in_premise = set(body_content) & set(parser.ALLOWED_FACTS)  # list de char
        self.fact_in_conclusion = set(head_content) & set(
            parser.ALLOWED_FACTS)  # idem (pas besoin des facts on se sert de fonction get fact

        # fire below only if in backwards inference it is used and used_rule False
        self.premise_node = None  # Rule as a Node flatten
        self.conclusion_clauses = set()  # set of clauses
        self.used_rule = False

        print(self.premise_content, self.conclusion_content, self.fact_in_premise, self.fact_in_conclusion)

    def fill_premise_node(self):
        self.premise_node = node_utils.Node(list_input=self.premise_content)

    def fill_conclusion_clauses(self):
        conclusion_node = node_utils.Node(list_input=self.conclusion_content)
        conclusion_node.transform_graph_and_or(conclusion_node)
        conclusion_node.transform_graph_cnf(conclusion_node)
        conclusion_node.flatten_graph_cnf()
        # A changer en set directement dans solver ?
        self.conclusion_clauses = solver.add_clause(conclusion_node)

        # if query or useful fact in fact_in_conclusion fire fill rule that fills premise_node, and
        # conclusion_clause_set --> dans autre classe
        # methode pour evaluer node avec set de facts (resolution clause avec inferred clauses)


class Graph:
    def __init__(self, rules_lst, facts_lst, queries_lst):
        self.facts_set = set()  # Facts
        self.rules_set = set()  # Rules
        self.inferred_clauses = set()  # ??

        for rule_content in rules_lst:
            symbol, index = node_utils.find_symbol_to_treat(rule_content)
            print(rule_content, index, symbol)
            if symbol == "=>":
                self.rules_set.add(Rule(rule_content[:index], rule_content[index + 1:]))
            elif symbol == "<=>":
                self.rules_set.add(Rule(rule_content[:index], rule_content[index + 1:]))
                self.rules_set.add(Rule(rule_content[index + 1:], rule_content[:index]))
            else:
                pass
                # mettre message erreur pour regler si pas d implication ??

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
