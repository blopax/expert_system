import argparse
import solver
import parser

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str, help="Name of the input file.\n")
    parser.add_argument("-i", "--interactive", action="store_true", help="Show the time needed to resolve the npuzzle.\n")
    parser.add_argument("-f", "--fast", action="store_true", help="Stop once queries are found, doesn't check for potential contradictions related.\n")
    parser.add_argument("-c", "--complete", action="store_true", help="Show if algorithm is complete. (All rules are horn clauses).\n")
    parser.add_argument("-r", "--resolution_mode", type=str, default="backward_chaining",
                        choices={"backward_chaining", "resolution"},
                        help="Define the resolution mode. Resolution is complete but doesn't change value of facts.\n")

    return parser.parse_args()


if __name__ == '__main__':
    try:
        args=get_args()
        filename = args.filename
        print(filename, args.interactive, args.fast)

        parse = parser.Parser(filename)
        rules_lst, facts_lst, queries_lst = parse.parse_file()
        new_facts = None
        if not args.interactive:
            string = solver.solve(rules_lst, facts_lst, queries_lst, new_facts)
            print(string, end='')
        else:
            if not rules_lst and not facts_lst and not queries_lst:
                keep_going = False
            else:
                keep_going = True
            input_error = False
            while keep_going:
                if input_error is False:
                    string = solver.solve(rules_lst, facts_lst, queries_lst, new_facts)
                    print(string, end='')
                new_facts = input("Press 'q' to quit or change facts here (only capitalize letters no spaces):\n")
                if new_facts == 'q':
                    keep_going = False
                else:
                    facts_list = list(new_facts)
                    if set(facts_list) <= set(parser.ALLOWED_FACTS):
                        new_facts = list(set(facts_list))
                        input_error = False
                    else:
                        input_error = True
                        print("\nWrong input, please try again.")

    except Exception as e:
        print(e)
        # if len(sys.argv) != 2:
        #     raise Exception(utils.INPUT_ERROR)
        # filename = sys.argv[1]

