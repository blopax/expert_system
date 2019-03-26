import parser
import sys

import node_utils
import utils


def add_literal_to_clause(node, clause):
    if node.content in parser.ALLOWED_FACTS:
        clause['positive_facts'] |= {node.content}
    elif node.content == '!':
        clause['negative_facts'] |= {node.children[0].content}
    return clause


def make_clause(node):
    node_utils.show_graph(node)
    clause = {
        'positive_facts': set(),
        'negative_facts': set()
    }
    if node.content in ['!'] + parser.ALLOWED_FACTS:
        clause = add_literal_to_clause(node, clause)
    if node.content == '|':
        for child in node.children:
            clause = add_literal_to_clause(child, clause)
    print(clause)
    return clause


def add_clause(node):
    clauses_list = []
    if node.content == '+':
        for child in node.children:
            clauses_list.append(make_clause(child))
    else:
        clauses_list = make_clause(node)
    return clauses_list


def check_horn_clauses(clauses_list):
    for clause in clauses_list:
        if len(clause['positive_facts']) > 1:
            return False
    return True


def resolution(clause_a, clause_b):
    # print("in")
    # print(type(clause_a), type(clause_b))
    new_clauses = []
    complementary_facts = clause_a['positive_facts'] & clause_b['negative_facts'] |\
                          clause_b['positive_facts'] & clause_a['negative_facts']
    for complementary_fact in complementary_facts:
        new_clause = dict()
        new_clause['positive_facts'] = (clause_a['positive_facts'] | clause_b['positive_facts']) - set(
            complementary_fact)
        new_clause['negative_facts'] = (clause_a['negative_facts'] | clause_b['negative_facts']) - set(
            complementary_fact)
        tautology = new_clause['positive_facts'] & new_clause['negative_facts']
        if not tautology:
            new_clauses.append(new_clause)
        # print("new clauses = {}".format(new_clauses))
    # print("out")
    return new_clauses


def check_query(query, clauses_list):
    query_is = 'Ambiguity'
    for item in clauses_list:
        if set(item['positive_facts']) == set(query) and not set(item['negative_facts']):
            if query_is == 'Ambiguity':
                query_is = "True"
            elif query_is == "False":
                query_is = 'Contradiction'
        elif not set(item['positive_facts']) and set(item['negative_facts']) == set(query):
            if query_is == 'Ambiguity':
                query_is = "False"
            elif query_is == "True":
                query_is = 'Contradiction'
    return query_is


def resolution_algo(knowledge_base, query):
    # KB = list_clauses
    if len(knowledge_base) <= 1:
        return check_query(query, knowledge_base)  # a preciser
    while True:
        print("KB = {}".format(knowledge_base, query))
        infered_kb = []
        extending_kb = False
        # print("\nkb = {}\n".format(knowledge_base))
        for index, clause_a in enumerate(knowledge_base[:-1]):
            for clause_b in knowledge_base[index+1:]:
                print(clause_a, clause_b)
                new_clauses = resolution(clause_a, clause_b)
                # query_in_new_clauses = check_query(query, new_clauses)
                # if isinstance(query_in_new_clauses, bool):
                #     print(clause_a, clause_b, new_clauses)
                #     return query_in_new_clauses
                # But = checker au fur et a mesure mais ne voit pas contradictions
                for item in new_clauses:
                    infered_kb.append(item)
                    infered_kb += new_clauses #.append(new_clauses)
        for item in infered_kb:
            if item not in knowledge_base:
                knowledge_base += [item]
                extending_kb = True
        if not extending_kb:
            return check_query(query, knowledge_base)  # None signifie ambiguity


# checker simplification KB (enlever ce qui est inclu dans l'autre, enlever doublons,
# enlever si on un des elts vrais en gros si set inclu dans un autre pr pos ET neg sert pour les 2


# query as a string
def backward_inference_motor(graph, query):
    if initial_check(graph, query):
        return initial_check(graph, query)
    look_premises_of = [query]
    infered_clauses = create_initial_infered_clauses(graph) # clauses that are True initially initial facts as clauses, later every time a fact becomes True or clauses with or
    while True:
        if check_fixed_point(): # look_premises_of didn't grow or query is True
            return appropriate_value

        for fact in look_premises_of:




def initial_check(graph, query):
    query_fact = graph.get_fact(query)
    if query_fact.value is True:
        return True
    if query not in graph.fact_in_conclusion:
        return False
    return None





if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise Exception(utils.INPUT_ERROR)
        file = sys.argv[1]
        parse = parser.Parser(file)
        rules_lst, facts_lst, queries_lst = parse.parse_file()
        list_input = []
        for i, x in enumerate(rules_lst):
            list_input = list_input + ['('] + x + [')']
            if i != len(rules_lst) - 1:
                list_input += ['+']
        # rule = ['A', '=>', 'B', '<=>', '!', '(', '!', '!', 'C', '+', '!', '!', 'D', ')', '+', 'A']
        rule = ['(', 'A', '=>', 'C', ')', '+', '(', 'C', '=>', 'B', ')', '+', 'A']
        # rule = ['(', 'A', '=>', 'C', ')' '+', '(', 'C', '=>', 'B', ')', '+', 'A'] pb ne voit pas manque , entre ) et +
        root = node_utils.Node(list_input=rule)
        root.transform_graph_and_or(root)
        root.transform_graph_cnf(root)
        node_utils.show_graph(root)
        root.flatten_graph_cnf()
        # node_utils.show_graph(root)
        cl_list = add_clause(root)
        print(cl_list)
        print(resolution(cl_list[0], cl_list[1]))
        # print("bob")
        print(resolution_algo(cl_list, 'B'))
    except Exception as e:
        print(e)

# ici peut etre pb d arbre avant resolution checker ces pbs de show graph flatten
