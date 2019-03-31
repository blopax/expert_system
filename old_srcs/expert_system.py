import sys
import os

from parsing import Parser
from node import Graph
from solver import Solver

class File:
    
    def __init__(self, file_name):
        self.parser = Parser(file_name)
        self.graph = Graph(self.parser)
        self.solver = Solver(self.parser, self.graph)

    def display_result(self):
        i = 0
        result = ""
        while i < len(self.parser.queries):
            if self.solver.lst_display_ok(self.parser.queries[i]) and self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].is_contradictory == False:
                self.solver.lst_display.append(self.parser.queries[i])
                result += self.parser.queries[i] + " is "
                if self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].status == "U":
                    result += "unknown.\n"
                elif self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].status == "F":
                    result += "false.\n"
                elif self.graph.struct_facts[self.graph.correspondance.get(self.parser.queries[i])].status == "T":
                    result += "true.\n"
            i += 1
        return result

def treat_entry(arg):
    if os.path.isfile(arg):
        fichier = File(arg)
        if fichier.parser.parse() and fichier.parser.rule_nb != 0 and fichier.parser.fact_nb == 1 and fichier.parser.queri_nb == 1:
            fichier.parser.distribute_conclusion()
            #fichier.display_data()
            fichier.parser.treat_rules()
            #fichier.display_polishes()
            fichier.graph.create_global_graph()
            #fichier.display_graph()
            fichier.solver.solve()
            return_str = fichier.display_result()
            #fichier.display_graph()
        else:
            return_str = "File " + arg + " not well formated."
    else:
        return_str = "File " + arg + " not found"
    return return_str

def main(argv):
    i = 0
    for arg in argv:
        if arg.find('.txt') > 0: #a checker
            print(treat_entry(arg))
        else:
            print("File " + arg + " not well formated. Please give .txt files only.")
        if i != len(argv) - 1:
            print("\n-----------------------------------\n")
        i += 1

if __name__ == "__main__":
    main(sys.argv[1:])
