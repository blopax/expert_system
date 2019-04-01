import sys

import node_utils
import resolution_solver
import parsing


class Fact:
    def __init__(self, content):
        self.content = content
        self.value = False
        self.confirmed = False
        self.triggered_by = None


class Clause:
    def __init__(self, positive_facts=None, negative_facts=None, node=None, confirmed=False):
        self.positive_facts = set()
        self.negative_facts = set()
        self.confirmed = confirmed
        self.value = False

        if positive_facts:
            self.positive_facts = positive_facts
        if negative_facts:
            self.negative_facts = negative_facts
        if node:
            self.make_clause(node)
        self.all_facts = self.positive_facts | self.negative_facts
        self.is_literal = len(self.all_facts) == 1

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
        if node.content in parsing.ALLOWED_FACTS:
            self.positive_facts |= {node.content}
        elif node.content == '!':
            self.negative_facts |= {node.children[0].content}

    def make_clause(self, node):
        if node.content in ['!'] + parsing.ALLOWED_FACTS:
            self.add_literal_to_clause(node)
        if node.content == '|':
            for child in node.children:
                self.add_literal_to_clause(child)

    def check_horn_clauses(self):
        if len(self.positive_facts) > 1:
            return False
        return True


class Rule:
    def __init__(self, rule_content, body_content, head_content):
        self.rule_content = rule_content
        self.premise_content = body_content
        self.conclusion_content = head_content
        self.fact_in_premise = set(body_content) & set(parsing.ALLOWED_FACTS)
        self.fact_in_conclusion = set(head_content) & set(parsing.ALLOWED_FACTS)
        self.premise_clauses = self.fill_clauses_from_content(self.premise_content)
        self.conclusion_clauses = self.fill_clauses_from_content(self.conclusion_content, confirmed=True)
        self.used_rule = False
        self.clauses_in_premise_all_confirmed = False
        self.triggered = -1

    @staticmethod
    def fill_clauses_from_content(content, confirmed=False):
        node = node_utils.Node(list_input=content)
        node.transform_graph_and_or(node)
        node.transform_graph_cnf(node)
        node.flatten_graph_cnf()
        return resolution_solver.add_clause(node, confirmed=confirmed)


class Graph:
    def __init__(self, rules_lst, facts_lst, queries_lst):
        self.facts_set = set()
        self.rules_set = set()
        self.confirmed_clauses = set()
        self.hypothesis_clauses = set()
        self.contradiction = None

        for rule_content in rules_lst:
            symbol, index = node_utils.find_symbol_to_treat(rule_content)
            if symbol == "=>":
                self.rules_set.add(Rule(rule_content, rule_content[:index], rule_content[index + 1:]))
            elif symbol == "<=>":
                self.rules_set.add(Rule(rule_content, rule_content[:index], rule_content[index + 1:]))
                self.rules_set.add(Rule(rule_content, rule_content[index + 1:], rule_content[:index]))

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
        self.update_confirmed_clauses()

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
            fact.triggered_by = 'Set by initial facts'
        facts_in_conclusions = set()
        for rule in self.rules_set:
            facts_in_conclusions.update(rule.fact_in_conclusion)
        facts_not_in_conclusions = fact_content_set.difference(facts_in_conclusions)
        for fact_not_in_conclusions in facts_not_in_conclusions:
            fact = self.get_fact(fact_not_in_conclusions)
            fact.confirmed = True
            fact.triggered_by = 'Set by initial facts'

    def get_confirmed_facts(self):
        confirmed_facts = set()
        for fact in self.facts_set:
            if fact.confirmed is True:
                confirmed_facts.add(fact.content)
        return confirmed_facts

    def update_confirmed_clauses(self):
        for fact in {self.get_fact(fact_content) for fact_content in self.get_confirmed_facts()}:
            if fact.value is False:
                clause = Clause(negative_facts=set(fact.content), confirmed=True)
            else:
                clause = Clause(positive_facts=set(fact.content), confirmed=True)
            already_exists = False
            for confirmed_clause in self.confirmed_clauses:
                if (clause.negative_facts == confirmed_clause.negative_facts
                        and clause.positive_facts == confirmed_clause.positive_facts):
                    already_exists = True
            if not already_exists:
                self.confirmed_clauses.add(clause)

    def get_facts_from_confirmed_clauses(self):
        confirmed_facts = set()
        for clause in self.confirmed_clauses:
            clause_facts = (clause.positive_facts | clause.negative_facts)
            if len(clause_facts) == 1:
                fact_content = clause_facts.pop()
                confirmed_facts.add(fact_content)
        return confirmed_facts


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise Exception(parsing.INPUT_ERROR)
        file = sys.argv[1]
        parse = parsing.Parser(file)
        rules_list, facts_list, queries_list = parse.parse_file()
        G = Graph(rules_list, facts_list, queries_list)

    except Exception as e:
        print(e)
