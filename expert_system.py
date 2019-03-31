import argparse
import solver
import parsing
import node_utils
import graph as graph_module


def check_if_rules_horn_clauses(rules_list):
    horn_clauses_only = True
    for rule_content in rules_list:
        node = node_utils.Node(list_input=rule_content)
        node.transform_graph_and_or(node)
        node.transform_graph_cnf(node)
        node.flatten_graph_cnf()
        if node.content == "+":
            horn_clauses_only = False
            break
        clause = graph_module.Clause(node=node)
        horn_clause = clause.check_horn_clauses()
        if not horn_clause:
            horn_clauses_only = False
            break
    return horn_clauses_only


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Name of the input file.\n")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Show the time needed to resolve the npuzzle.\n")
    parser.add_argument("-f", "--fast", action="store_true",
                        help="Stop once queries are found, doesn't check for potential contradictions related.\n")
    parser.add_argument("-c", "--complete", action="store_true",
                        help="Show if algorithm is complete. (All rules are horn clauses).\n")
    parser.add_argument("-r", "--resolution_mode", type=str, default="backward_chaining",
                        choices={"backward_chaining", "resolution"},
                        help="Define the resolution mode. Resolution is complete but doesn't change value of facts.\n")
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_args()
        filename = args.filename

        parse = parsing.Parser(filename)
        rules_lst, facts_lst, queries_lst = parse.parse_file()

        if args.complete and args.resolution_mode == "backward_chaining":
            complete = check_if_rules_horn_clauses(rules_lst)
            if not complete:
                print("Be aware: some rules are not Horn Clauses. The backward_chaining algorithm is not complete.\n")

        new_facts = None
        if not args.interactive:
            string = solver.solve(rules_lst, facts_lst, queries_lst, new_facts, args.fast)
            print(string, end='')
        else:
            if not rules_lst and not facts_lst and not queries_lst:
                keep_going = False
            else:
                keep_going = True
            input_error = False
            while keep_going:
                if input_error is False:
                    string = solver.solve(rules_lst, facts_lst, queries_lst, new_facts, args.fast)
                    print(string, end='')
                new_facts = input("Press 'q' to quit or change facts here (only capitalize letters no spaces):\n")
                if new_facts == 'q':
                    keep_going = False
                else:
                    facts_list = list(new_facts)
                    if set(facts_list) <= set(parsing.ALLOWED_FACTS):
                        new_facts = list(set(facts_list))
                        input_error = False
                    else:
                        input_error = True
                        print("\nWrong input, please try again.")

    except Exception as e:
        print(e)
