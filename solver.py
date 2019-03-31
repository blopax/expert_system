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


def resolution(clause_a, clause_b):
    new_clauses = []
    complementary_facts = (clause_a.positive_facts & clause_b.negative_facts
                           | clause_b.positive_facts & clause_a.negative_facts)
    for complementary_fact in complementary_facts:
        new_clause = graph_module.Clause()
        new_clause.positive_facts = (clause_a.positive_facts | clause_b.positive_facts) - set(complementary_fact)
        new_clause.negative_facts = (clause_a.negative_facts | clause_b.negative_facts) - set(complementary_fact)
        tautology = new_clause.positive_facts & new_clause.negative_facts
        if not tautology:
            new_clauses.append(new_clause)
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
        infered_kb = []
        extending_kb = False
        for index, clause_a in enumerate(knowledge_base[:-1]):
            for clause_b in knowledge_base[index + 1:]:
                new_clauses = resolution(clause_a, clause_b)
                for item in set(new_clauses):
                    infered_kb.append(item)
        for infered_clause in set(infered_kb):
            infered_clause_is_new = True
            for confirmed_clause in set(knowledge_base):
                same_positive = (infered_clause.positive_facts == confirmed_clause.positive_facts)
                same_negative = (infered_clause.negative_facts == confirmed_clause.negative_facts)
                if same_positive and same_negative:
                    infered_clause_is_new = False
                    break
            if infered_clause_is_new is True:
                knowledge_base += [infered_clause]
                extending_kb = True
        if not extending_kb:
            return knowledge_base


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


def solve(rules_lst, facts_lst, queries_lst, facts_input=None, fast=None):
    if facts_input:
        facts_lst = facts_input

    g = graph_module.Graph(rules_lst, facts_lst, queries_lst)
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

        # ################
        # #Resolution
        # list_input = []
        # # for i, x in enumerate(rules_lst):
        # #     list_input = list_input + ['('] + x + [')']
        # #     if i != len(rules_lst) - 1:
        # #         list_input += ['+']
        # # root = node_utils.Node(list_input=list_input)
        # import node_utils
        # # rule_example = ['A', '=>', 'B', '<=>', '!', '(', '!', '!', 'C', '+', '!', '!', 'D', ')', '+', 'A']
        # # rule_example = ['(', 'A', '=>', 'C', ')', '+', '(', 'C', '=>', 'B', ')', '+', 'A']
        # # rule_example = ['(', 'A', '=>', 'C', ')' '+', '(', 'C', '=>', 'B', ')', '+', 'A']
        # rule_example = ['C', '+', '!', '(', '!', 'B', '+', 'H', '+', '!', '(', '!', '(', 'A', '+', 'G', ')', '+',
        # 'D', ')', ')', '+', 'A', '+', 'B']
        # # pb ne voit pas manque , entre ) et +
        # root = node_utils.Node(list_input=rule_example)
        # root.transform_graph_and_or(root)
        # root.transform_graph_cnf(root)
        # root.flatten_graph_cnf()
        # node_utils.show_graph(root)
        # # node_utils.show_graph(root)
        # cl_list = add_clause(root)
        # #cl_list.append(graph.Clause(positive_facts={'A'}))
        # #cl_list.append(graph.Clause(positive_facts={'C'}))
        # print(resolution_algo(cl_list, 'D'))
        # # ################

    except Exception as e:
        print(e)
