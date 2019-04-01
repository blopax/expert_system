import parsing

import resolution_solver
import graph as graph_module
import copy


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
        update_facts(graph, rule)
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


def update_facts(graph, rule):
    new_confirmed_clauses = rule.conclusion_clauses
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
                    fact.triggered_by = "Triggered by rule {}".format("".join(rule.rule_content))
                elif fact and fact.value is not True:
                    graph.contradiction = fact.content
            else:
                fact_content = None
                for fact_content in clause.negative_facts:
                    break
                fact = graph.get_fact(fact_content)
                if fact and fact.confirmed is False:
                    fact.confirmed = True
                    fact.triggered_by = "Triggered by rule {}".format("".join(rule.rule_content))
                elif fact and fact.value is True:
                    graph.contradiction = fact_content


def define_outcome(g, queries_lst, advice, proof):
    ambiguity_clauses = {clause for clause in g.confirmed_clauses if clause.is_literal is False}
    confirmed_facts_positive = {fact for fact in g.facts_set if fact.confirmed is True and fact.value is True}
    confirmed_facts_negative = {fact for fact in g.facts_set if fact.confirmed is True and fact.value is False}
    confirmed_facts_clauses = ({graph_module.Clause(positive_facts={fact.content}) for fact in confirmed_facts_positive}
                               | {graph_module.Clause(negative_facts={fact.content}) for fact in
                                  confirmed_facts_negative})
    knowledge_base = list(ambiguity_clauses | confirmed_facts_clauses)
    return resolution_solver.display_queries(g, knowledge_base, queries_lst, advice, proof, mode='backward_chaining')


def backward_chaining_solve(rules_lst, facts_lst, queries_lst, facts_input=None, fast=None, advice=False, proof=False):
    if facts_input:
        facts_lst = facts_input
    g = graph_module.Graph(rules_lst, facts_lst, queries_lst)

    g = backward_inference_motor(g, set(queries_lst), fast)
    if g.contradiction:
        display_string = "Contradiction on fact {}.\n".format(g.contradiction)
    else:
        display_string = define_outcome(g, queries_lst, advice, proof)
    return display_string


def treat_entry(filename, facts_input=None, mode='backward_chaining'):
    parse = parsing.Parser(filename)
    rules_lst, facts_lst, queries_lst = parse.parse_file()
    if mode == 'backward_chaining':
        return backward_chaining_solve(rules_lst, facts_lst, queries_lst, facts_input)
    else:
        return resolution_solver.resolution_solve(rules_lst, facts_lst, queries_lst, facts_input)
