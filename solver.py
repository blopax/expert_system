import parsing
import sys

import utils
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


def check_query(query, clauses_list):
    for clause in clauses_list:
        tautaology = False
        for literal_clause in [clause_item for clause_item in clauses_list if
                               len(clause_item.positive_facts | clause_item.negative_facts) == 1]:
            if (literal_clause.positive_facts <= clause.positive_facts
                    and literal_clause.negative_facts <= clause.negative_facts):
                tautaology = True
        if clause.positive_facts == {query.content} and not clause.negative_facts:
            query.value = True
            query.confirmed = True
            query.outcome = 'true'
        elif query.content in clause.positive_facts and query.confirmed is not True and not tautaology:
            query.outcome = 'ambiguous'
    if query.outcome is None:
        query.outcome = str(query.value).lower()
    return query


def resolution_algo(knowledge_base, query):
    if len(knowledge_base) <= 1:
        return check_query(query, knowledge_base)
    knowledge_base = resolution_knowledge_base(knowledge_base)
    return check_query(query, knowledge_base)


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
        if len(clause_a.all_facts) ==0:
            pass
        for clause_b in knowledge_base[index + 1:]:
            if len(clause_b.all_facts) ==0:
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


def backward_inference_motor(graph, queries, fast=None):
    all_queries_confirmed = check_queries_confirmed(graph, queries, True)
    facts_of_interests = copy.deepcopy(queries)  # set of facts_content
    queue = add_rules_to_queue(graph, None, facts_of_interests)  # list of rules
    queue.sort(key=lambda rule_item: rule_triggered(rule_item, graph.confirmed_clauses), reverse=True)
    rotate = 0

    while queue and not all_queries_confirmed and not graph.contradiction and rotate <= len(queue):
        rule = queue.pop(0)
        queue, facts_of_interests, rotation = apply_rule(graph, rule, queue, facts_of_interests)

        if rotation:
            rotate += 1
            graph, rotate, facts_of_interests = check_queue_rotation(graph, queue, facts_of_interests, rotate, queries)
        else:
            rotate = 0
        all_queries_confirmed = check_queries_confirmed(graph, queries, True)

    if not fast:
        while queue and rule_triggered(queue[0], graph.confirmed_clauses, False) == 1 and not graph.contradiction:
            rule = queue.pop(0)
            queue, facts_of_interests, rotation = apply_rule(graph, rule, queue, facts_of_interests)
    return graph


def check_queue_rotation(graph, queue, facts_of_interests, rotate, queries):
    if rotate == len(queue) and facts_of_interests:
        confirmed_facts = graph.get_facts_from_confirmed_clauses()
        facts_of_interests = facts_of_interests - confirmed_facts

        fact_item_content = None
        new_graph = None
        for fact_item_content in facts_of_interests:
            new_graph = copy.deepcopy(graph)
            if {fact_item_content} not in [x.negative_facts for x in graph.confirmed_clauses]:
                new_graph.confirmed_clauses.add(graph_module.Clause(negative_facts=set(fact_item_content)))
            new_graph = backward_inference_motor(new_graph, queries)
            if not new_graph.contradiction:
                rotate = 0
                break
        facts_of_interests.remove(fact_item_content)
        if fact_item_content:
            graph = new_graph
            graph.update_confirmed_clauses()
            queue.sort(key=lambda rule_item: rule_triggered(rule_item, graph.confirmed_clauses), reverse=True)
    return graph, rotate, facts_of_interests


def apply_rule(graph, rule, queue, facts_of_interests):
    rotation = 0
    trigger = rule_triggered(rule, graph.confirmed_clauses)
    if trigger == 1:
        graph.confirmed_clauses.update(copy.deepcopy(rule.conclusion_clauses))
        update_facts(graph, rule.conclusion_clauses)
        new_facts_of_interests = rule.fact_in_conclusion - facts_of_interests
        facts_of_interests.update(new_facts_of_interests)
        add_rules_to_queue(graph, queue, new_facts_of_interests)
        queue.sort(key=lambda rule_item: rule_triggered(rule_item, graph.confirmed_clauses), reverse=True)
    elif trigger == 0:
        pass
    elif trigger == -1:
        new_facts_of_interests = rule.fact_in_premise - facts_of_interests
        facts_of_interests.update(new_facts_of_interests)
        queue.append(rule)
        rotation = 1
        old_queue_length = len(queue)
        if len(add_rules_to_queue(graph, queue, new_facts_of_interests)) > old_queue_length:
            queue.sort(key=lambda rule_item: rule_triggered(rule_item, graph.confirmed_clauses), reverse=True)
            rotation = 0
    confirmed_facts = graph.get_confirmed_facts()
    facts_of_interests = facts_of_interests - confirmed_facts
    return queue, facts_of_interests, rotation


def rule_triggered(rule, confirmed_clauses, change_rule=True):
    trigger = 1
    for clause in rule.premise_clauses:
        if clause.confirmed is False:
            clause.update_clause_attributes(confirmed_clauses)
        if clause.value is False and clause.confirmed is True:
            trigger = 0
            break
        elif clause.confirmed is False:
            trigger = -1
            break
    if change_rule:
        rule.triggered = trigger
    return trigger


def check_queries_confirmed(graph, queries, initial=False):
    all_queries_confirmed = True
    for query in queries:
        query_fact = graph.get_fact(query)
        if initial and query not in graph.facts_in_rules_conclusions:
            query_fact.confirmed = True
        if query_fact.confirmed is False:
            all_queries_confirmed = False
            break
    return all_queries_confirmed


def add_rules_to_queue(graph, queue, new_facts_of_interests):
    if queue is None:
        queue = []
    for fact_content in new_facts_of_interests:
        for rule in graph.rules_set:
            if fact_content in rule.fact_in_conclusion and rule.triggered == -1 and rule not in queue:
                queue.append(rule)
    return queue


def update_facts(graph, new_confirmed_clauses):
    for clause in new_confirmed_clauses:
        if clause.is_literal is True:
            if len(clause.positive_facts) == 1:
                fact_content = None
                for fact_content in clause.positive_facts:
                    break
                fact = graph.get_fact(fact_content)
                if fact and fact.confirmed is False:
                    fact.value = True
                    fact.confirmed = True
                elif fact and fact.value is not True:
                    graph.contradiction = fact.content
            else:
                fact_content = None
                for fact_content in clause.negative_facts:
                    break
                fact = graph.get_fact(fact_content)
                if fact and fact.confirmed is False:
                    fact.confirmed = True
                elif fact and fact.value is True:
                    graph.contradiction = fact_content


def define_outcome(graph, queries_lst):
    fact_queries_set = {graph.get_fact(fact_content) for fact_content in queries_lst}
    for fact in graph.facts_set & fact_queries_set:
        if fact.confirmed is False:
            check_ambiguity(graph, fact)
        else:
            fact.outcome = str(fact.value).lower()


def check_ambiguity(graph, fact):
    ambiguity_clauses = {clause for clause in graph.confirmed_clauses if clause.is_literal is False}
    confirmed_facts_positive = {fact for fact in graph.facts_set if fact.confirmed is True and fact.value is True}
    confirmed_facts_negative = {fact for fact in graph.facts_set if fact.confirmed is True and fact.value is False}
    confirmed_facts_clauses = ({graph_module.Clause(positive_facts={fact.content}) for fact in confirmed_facts_positive}
                               | {graph_module.Clause(negative_facts={fact.content}) for fact in
                                  confirmed_facts_negative})
    knowledge_base = list(ambiguity_clauses | confirmed_facts_clauses)
    return resolution_algo(knowledge_base, fact)


def solve(rules_lst, facts_lst, queries_lst, facts_input=None,
          fast=None, resolution_mode='backward_chaining', initially_false=None):
    if facts_input:
        facts_lst = facts_input

    g = graph_module.Graph(rules_lst, facts_lst, queries_lst)

    if resolution_mode == 'resolution':
        initial_knowledge_base = initialize_resolution(g, initially_false)
        knowledge_base = resolution_knowledge_base(initial_knowledge_base)
        g.contradiction = contradiction_in_kb(knowledge_base)
        if g.contradiction:
            display_string = "Contradiction on fact {}.\n".format(g.contradiction)
        else:
            display_string = display_queries(knowledge_base, queries_lst)
    else:
        g = backward_inference_motor(g, set(queries_lst), fast)
        if g.contradiction:
            display_string = "Contradiction on fact {}.\n".format(g.contradiction)
        else:
            define_outcome(g, queries_lst)
            display_string = ""
            for query in queries_lst:
                fact = g.get_fact(query)
                display_string += "{} is {}.\n".format(query, str(fact.outcome))
    return display_string


def treat_entry(filename, facts_input=None):
    parse = parsing.Parser(filename)
    rules_lst, facts_lst, queries_lst = parse.parse_file()
    return solve(rules_lst, facts_lst, queries_lst, facts_input)


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise Exception(utils.INPUT_ERROR)
        filepath = sys.argv[1]
        parser = parsing.Parser(filepath)
        rules_list, facts_list, queries_list = parser.parse_file()

    except Exception as e:
        print(e)
