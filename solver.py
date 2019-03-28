import parser
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


def check_horn_clauses(clauses_list):
    for clause in clauses_list:
        if len(clause['positive_facts']) > 1:
            return False
    return True


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
    query_is = 'Ambiguity'
    for item in clauses_list:
        if item.positive_facts == set(query) and not item.negative_facts:
            if query_is == 'Ambiguity':
                query_is = "True"
            elif query_is == "False":
                query_is = 'Contradiction'
        elif not item.positive_facts and item.negative_facts == set(query):
            if query_is == 'Ambiguity':
                query_is = "False"
            elif query_is == "True":
                query_is = 'Contradiction'
    return query_is


def resolution_algo(knowledge_base, query):
    if len(knowledge_base) <= 1:
        return check_query(query, knowledge_base)  # a preciser
    while True:
        infered_kb = []
        extending_kb = False
        for index, clause_a in enumerate(knowledge_base[:-1]):
            for clause_b in knowledge_base[index + 1:]:
                new_clauses = resolution(clause_a, clause_b)
                # query_in_new_clauses = check_query(query, new_clauses)
                # if isinstance(query_in_new_clauses, bool):
                #     print(clause_a, clause_b, new_clauses)
                #     return query_in_new_clauses
                # But = checker au fur et a mesure mais ne voit pas contradictions
                for item in set(new_clauses):
                    infered_kb.append(item)
                    # infered_kb += new_clauses #.append(new_clauses)
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
            return check_query(query, knowledge_base)  # None signifie ambiguity

# checker simplification KB (enlever ce qui est inclu dans l'autre, enlever doublons,
# enlever si on un des elts vrais en gros si set inclu dans un autre pr pos ET neg sert pour les 2


def backward_inference_motor(graph, queries):
    all_queries_confirmed = check_queries_confirmed(graph, queries, True)
    facts_of_interests = queries  # set of facts_content
    confirmed_clauses = initial_confirmed_clauses(graph)  # set of Clauses
    # confirmed_facts = graph.get_confirmed_facts()
    _, queue = add_rules_to_queue(graph, [], facts_of_interests)  # list of rules
    queue.sort(key=lambda rule_item: rule_triggered(rule_item, confirmed_clauses), reverse=True)
    rotate = 0

    count = 0
    while queue and not all_queries_confirmed:
        count += 1
        queue_length_before = len(queue)
        rule = queue.pop(0)
        queue, facts_of_interests, confirmed_clauses = apply_rule(graph, rule,
                                                                  queue, facts_of_interests, confirmed_clauses)

        # mettre dans fonction separee
        if len(queue) == queue_length_before:
            rotate += 1
        else:
            rotate = 0

        if rotate == len(queue) and facts_of_interests:
            confirmed_facts = graph.get_confirmed_facts()
            facts_to_confirm = facts_of_interests - confirmed_facts
            fact_content = None
            for fact_content in facts_to_confirm:
                break
            fact = graph.get_fact(fact_content)
            fact.confirmed = True
            queue.sort(key=lambda rule_item: rule_triggered(rule_item, confirmed_clauses), reverse=True)
            rotate = 0

        # confirmed_facts = graph.get_confirmed_facts()
        all_queries_confirmed = check_queries_confirmed(graph, queries, True)

    # return graph


def apply_rule(graph, rule, queue, facts_of_interests, confirmed_clauses):
    trigger = rule_triggered(rule, confirmed_clauses)
    if trigger == 1:  # 'rule_body_confirmed_true'
        confirmed_clauses.update(copy.deepcopy(rule.conclusion_clauses))
        update_facts(graph, rule.conclusion_clauses)
        queue.sort(key=lambda rule_item: rule_triggered(rule_item, confirmed_clauses))
    elif trigger == 0:  # 'rule_body_confirmed_false':
        pass
    elif trigger == -1:  # 'rule_body_not_confirmed':
        new_facts_of_interests = rule.fact_in_premise - facts_of_interests
        facts_of_interests.update(new_facts_of_interests)
        queue.append(rule)
        if add_rules_to_queue(graph, queue, new_facts_of_interests)[0] >= 1:
            queue.sort(key=lambda rule_item: rule_triggered(rule_item, confirmed_clauses), reverse=True)
    confirmed_facts = graph.get_confirmed_facts()
    facts_of_interests = facts_of_interests - confirmed_facts
    return queue, facts_of_interests, confirmed_clauses


def rule_triggered(rule, confirmed_clauses):
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
    nb_rules_added = 0
    for fact_content in new_facts_of_interests:
        for rule in graph.rules_set:
            if fact_content in rule.fact_in_conclusion and rule.triggered == -1 and rule not in queue:
                queue.append(rule)
                nb_rules_added += 1
    return nb_rules_added, queue


def update_facts(graph, new_confirmed_clauses):
    for clause in new_confirmed_clauses:
        if clause.is_literal is True:
            if len(clause.positive_facts) == 1:
                fact_content = None
                for fact_content in clause.positive_facts:
                    break
                fact = graph.get_fact(fact_content)
                if fact.confirmed is False:
                    fact.value = True
                    fact.confirmed = True
                elif fact.value is not True:
                    print("Contradiction on fact {}".format(fact.content))
            else:
                fact_content = None
                for fact_content in clause.negative_facts:
                    break
                fact = graph.get_fact(fact_content)
                if fact.confirmed is False:
                    fact.confirmed = True
                elif fact.value is True:
                    print("Contradiction on fact {}".format(fact.content))


def initial_confirmed_clauses(graph):
    confirmed_clauses = set()
    for fact in graph.facts_set:
        if fact.confirmed is True:
            if fact.value is False:
                clause = graph_module.Clause(negative_facts=set(fact.content), confirmed=True)
            else:
                clause = graph_module.Clause(positive_facts=set(fact.content), confirmed=True)
            confirmed_clauses.add(clause)
    return confirmed_clauses


def treat_entry(filename):
    parse = parser.Parser(filename)
    rules_lst, facts_lst, queries_lst = parse.parse_file()

    ###############
    # Backward_chaining
    g = graph_module.Graph(rules_lst, facts_lst, queries_lst)
    backward_inference_motor(g, set(queries_lst))

    display_string = ""
    for query in queries_lst:
        fact = g.get_fact(query)
        display_string += "{} is {}.\n".format(query, str(fact.value).lower())
    return display_string

    ###############


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise Exception(utils.INPUT_ERROR)
        file = sys.argv[1]

        string = treat_entry(file)
        print(string, end='')

        # ################
        # #Resolution
        # list_input = []
        # for i, x in enumerate(rules_lst):
        #     list_input = list_input + ['('] + x + [')']
        #     if i != len(rules_lst) - 1:
        #         list_input += ['+']
        # root = node_utils.Node(list_input=list_input)
        #
        # # rule_example = ['A', '=>', 'B', '<=>', '!', '(', '!', '!', 'C', '+', '!', '!', 'D', ')', '+', 'A']
        # # rule_example = ['(', 'A', '=>', 'C', ')', '+', '(', 'C', '=>', 'B', ')', '+', 'A']
        # # rule_example = ['(', 'A', '=>', 'C', ')' '+', '(', 'C', '=>', 'B', ')', '+', 'A']
        # pb ne voit pas manque , entre ) et +
        # # root = node_utils.Node(list_input=rule_example)
        # root.transform_graph_and_or(root)
        # root.transform_graph_cnf(root)
        # root.flatten_graph_cnf()
        # node_utils.show_graph(root)
        # # node_utils.show_graph(root)
        # cl_list = add_clause(root)
        # cl_list.append(graph.Clause(positive_facts={'A'}))
        # cl_list.append(graph.Clause(positive_facts={'C'}))
        # print(resolution_algo(cl_list, 'B'))
        # ################

    except Exception as e:
        print(e)
    # ici peut etre pb d arbre avant resolution checker ces pbs de show graph flatten
