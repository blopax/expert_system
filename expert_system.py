import argparse
import backward_chaining_solver
import resolution_solver
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
                        help="For backward chaining mode. Stop once queries are found, "
                             "doesn't check for potential contradictions related.\n")
    parser.add_argument("-a", "--advice", action="store_true",
                        help="Give advice for setting initial facts if ambiguity.\n")
    parser.add_argument("-c", "--complete", action="store_true",
                        help="Show if algorithm is complete. (All rules are horn clauses).\n")
    parser.add_argument("-p", "--proof", action="store_true",
                        help="Show proof for backward chaining mode. (All rules should be horn clauses).\n")
    parser.add_argument("-m", "--resolution_mode", type=str, default="backward_chaining",
                        choices={"backward_chaining", "resolution"},
                        help="Define the resolution mode. Resolution is complete but doesn't change value of facts.\n")
    return parser.parse_args()


def backward_chaining_algorithm(rules_list, facts_list, queries_list, args):
    new_facts = None
    if not args.interactive:
        string = backward_chaining_solver.backward_chaining_solve(rules_list, facts_list, queries_list, new_facts,
                                                                  fast=args.fast, advice=args.advice, proof=args.proof)
        print(string, end='')
    else:
        input_error = False
        keep_going = True
        if not rules_list and not facts_list and not queries_list:
            keep_going = False
        while keep_going:
            if input_error is False:
                string = backward_chaining_solver.backward_chaining_solve(rules_list, facts_list, queries_list,
                                                                          new_facts, fast=args.fast, proof=args.proof)
                print("{}".format(string), end='')
            new_facts = input("\nPress 'q' to quit or change initial fact. Please provide facts that are true here "
                              "(only capitalize letters no spaces):\n")
            if new_facts == 'q':
                keep_going = False
            else:
                print()
                facts_list = list(new_facts)
                if set(facts_list) <= set(parsing.ALLOWED_FACTS):
                    new_facts = list(set(facts_list))
                    input_error = False
                else:
                    input_error = True
                    print("\nWrong input, please try again.")


def resolution_algorithm(rules_list, facts_list, queries_list, args):
    new_facts = None
    initially_false = None
    keep_going = True
    input_error = False

    if not rules_list and not facts_list and not queries_list:
        keep_going = False
    while keep_going:
        if input_error is False:
            initially_false_error = True
            while initially_false_error:
                user_input = input("Please provide facts that are false here (only capitalize letters no spaces):\n")
                initially_false = list(set(user_input))
                if set(initially_false) <= set(parsing.ALLOWED_FACTS):
                    initially_false_error = False
            string = resolution_solver.resolution_solve(rules_list, facts_list, queries_list, facts_input=new_facts,
                                                        initially_false=initially_false, display=args.advice)
            print("\n{}".format(string), end='')
        if not args.interactive:
            keep_going = False
        else:
            new_facts = input("\nPress 'q' to quit or change initial fact. Please provide facts that are true here "
                              "(only capitalize letters no spaces):\n")
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


if __name__ == '__main__':
    try:
        options = get_args()
        filename = options.filename

        parse = parsing.Parser(filename)
        rules_lst, facts_lst, queries_lst = parse.parse_file()

        if (options.complete or options.proof) and options.resolution_mode == "backward_chaining":
            complete = check_if_rules_horn_clauses(rules_lst)
            if not complete:
                print("Be aware: some rules are not Horn Clauses. The backward_chaining algorithm is not complete.")
                if options.proof:
                    print("The proof may therefore be incomplete. It should work most of the time for simple proofs.\n")
                else:
                    print()

        if options.resolution_mode == 'backward_chaining':
            backward_chaining_algorithm(rules_lst, facts_lst, queries_lst, options)
        else:
            resolution_algorithm(rules_lst, facts_lst, queries_lst, options)

    except Exception as e:
        print(e)
