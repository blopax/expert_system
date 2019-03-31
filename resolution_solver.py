import graph as graph_module
import copy


def add_clause(node, confirmed=False):
    clauses_list = []
    if node.content == '+':
        for child in node.children:
            clause = graph_module.Clause(node=child, confirmed=confirmed)
            clauses_list.append(clause)
    else:
        clause = graph_module.Clause(node=node, confirmed=confirmed)
        clauses_list.append(clause)
    return clauses_list


def check_query(query, clauses_list):
    for clause in clauses_list:
        tautology = False
        for literal_clause in [clause_item for clause_item in clauses_list if len(clause_item.all_facts) == 1]:
            if (literal_clause.positive_facts <= clause.positive_facts
                    and literal_clause.negative_facts <= clause.negative_facts):
                tautology = True
        if clause.positive_facts == {query.content} and not clause.negative_facts:
            query.value = True
            query.confirmed = True
            query.outcome = 'true'
        elif query.content in clause.positive_facts and query.confirmed is not True and not tautology:
            query.outcome = 'ambiguous'
    if query.outcome is None:
        query.outcome = str(query.value).lower()
    return query


def resolution(clause_a, clause_b, knowledge_base):
    new_clauses = []
    if clause_a.is_literal and clause_b.is_literal:
        return new_clauses
    complementary_facts = (clause_a.positive_facts & clause_b.negative_facts
                           | clause_b.positive_facts & clause_a.negative_facts)
    for complementary_fact in complementary_facts:
        positive_facts = (clause_a.positive_facts | clause_b.positive_facts) - set(complementary_fact)
        negative_facts = (clause_a.negative_facts | clause_b.negative_facts) - set(complementary_fact)
        tautology = positive_facts & negative_facts
        if not tautology:
            new = True
            for clause in knowledge_base:
                if positive_facts >= clause.positive_facts and negative_facts >= clause.negative_facts:
                    new = False
                    break
            if new is True:
                new_clauses.append(graph_module.Clause(positive_facts=positive_facts, negative_facts=negative_facts))
    return new_clauses


def resolution_knowledge_base(knowledge_base):
    while True:
        extending_kb = False
        for index, clause_a in enumerate(knowledge_base[:-1]):
            for clause_b in knowledge_base[index + 1:]:
                new_clauses = resolution(clause_a, clause_b, knowledge_base)
                if new_clauses:
                    extending_kb = True
                    knowledge_base += new_clauses
        knowledge_base = clean_resolution(knowledge_base)
        if not extending_kb:
            return knowledge_base


def resolution_algo(knowledge_base, query):
    if len(knowledge_base) <= 1:
        return check_query(query, knowledge_base)
    knowledge_base = resolution_knowledge_base(knowledge_base)
    return check_query(query, knowledge_base)


def initialize_resolution(g, initially_false_facts):
    kb = set()
    if initially_false_facts is None:
        initially_false_facts = []
    for rule in g.rules_set:
        kb.update(rule.fill_clauses_from_content(rule.rule_content, confirmed=True))
    for true_fact_content in g.get_confirmed_facts():
        fact = g.get_fact(true_fact_content)
        if fact.value is True:
            kb.add(graph_module.Clause(positive_facts={true_fact_content}, confirmed=True))
    for false_fact_content in initially_false_facts:
        kb.add(graph_module.Clause(negative_facts={false_fact_content}, confirmed=True))
    return list(kb)


def clean_resolution(knowledge_base):
    useless_clauses = []
    for index, clause_a in enumerate(knowledge_base[:-1]):
        if len(clause_a.all_facts) == 0:
            pass
        for clause_b in knowledge_base[index + 1:]:
            if len(clause_b.all_facts) == 0:
                pass
            if (clause_a.positive_facts.issubset(clause_b.positive_facts)
                    and clause_a.negative_facts.issubset(clause_b.negative_facts)):
                useless_clauses.append(clause_b)
            elif (clause_b.positive_facts.issubset(clause_a.positive_facts)
                  and clause_b.negative_facts.issubset(clause_a.negative_facts)):
                useless_clauses.append(clause_a)
    for useless_clause in useless_clauses:
        if useless_clause in knowledge_base:
            knowledge_base.remove(useless_clause)
    return knowledge_base


def contradiction_in_kb(knowledge_base):
    contradiction = None
    kb_only_literals = [clause for clause in knowledge_base if clause.is_literal]
    for index, clause_a in enumerate(kb_only_literals[:-1]):
        for clause_b in kb_only_literals[index + 1:]:
            if (len(clause_a.positive_facts) == 1 and clause_a.positive_facts == clause_b.negative_facts
                    or len(clause_a.negative_facts) == 1 and clause_a.negative_facts == clause_b.positive_facts):
                contradiction = clause_a.all_facts.pop()
                return contradiction
    return contradiction


def display_queries(knowledge_base, queries_lst):
    display_string = ""
    kb_only_literals = [clause for clause in knowledge_base if clause.is_literal]
    queries_lst_copy = copy.deepcopy(queries_lst)
    for clause in kb_only_literals:
        literal = list(clause.all_facts)[0]
        if literal in queries_lst:
            if len(clause.positive_facts):
                display_string += "{} is {}.\n".format(literal, 'true')
            else:
                display_string += "{} is {}.\n".format(literal, 'negative')
            queries_lst_copy.remove(literal)
    for query in queries_lst_copy:
        display_string += "{} is {}.\n".format(query, 'ambiguous')

    return display_string


def resolution_solve(rules_lst, facts_lst, queries_lst, facts_input=None, initially_false=None):
    if facts_input:
        facts_lst = facts_input

    g = graph_module.Graph(rules_lst, facts_lst, queries_lst)

    initial_knowledge_base = initialize_resolution(g, initially_false)
    knowledge_base = resolution_knowledge_base(initial_knowledge_base)
    g.contradiction = contradiction_in_kb(knowledge_base)
    if g.contradiction:
        display_string = "Contradiction on fact {}.\n".format(g.contradiction)
    else:
        display_string = display_queries(knowledge_base, queries_lst)

    return display_string
