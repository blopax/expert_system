import sys
import os

global test_on
test_on = False

class File:
    
    def __init__(self, file_name):
        with open(file_name, "r") as opened_file:
            read_file = opened_file.read()
            self.lines = read_file.split("\n")
        self.rule_nb = 0

    def display_lines(self):
        i = 0
        while i < len(self.lines):
            print(self.lines[i])
            i = i + 1

    def is_imply(self, line, i):
        if i + 1 < len(line) and line[i] == '=' and line[i + 1] == '>':
            return True
        elif i - 1 >= 0 and  line[i - 1] == '=' and line[i] == '>':
            return True
        else:
            return False

    def is_logical(self, c, line, i):
        if c != '(' and c != ')' and c != '!' and c != '+' and c != '|' and c != '^' and self.is_imply(line, i) == False:
            return False
        else:
            return True

    def rule_is_ok(self, line, i):
    #at least one A, one => and one B
    #check if ! followed by str
    #check if ( matches )
    #check if () contains stuff
    #check if + or | or ^ are between strings
        nb_a = 0
        nb_b = 0
        nb_implies = 0
        if i == 1 and self.rule_nb == 0:
            print("line : " + line + "\t\tError format: No newline before facts when no comments.")
            return False
        elif i > 1:
            if self.lines[i - 1] != '' and self.rule_nb == 0:
                print("line : " + line + "\t\tError format: No newline before facts.")
                return False
        if self.rule_nb > 0 and i > 0 and self.lines[i - 1] != '':
            if self.lines[i - 1][0].isalpha() == False and self.lines[i - 1][0] != '!' and self.lines[i - 1][0] != '(':
                print ("line : " + line + "\t\tError format: all facts must be in one block.")
                return False
        j = 0
        while j < len(line) and line[j] != '#':
            if line[j].isalpha() == False and self.is_logical(line[j], line, j) == False and line[j] != ' ' and line[j] != '\t':
                print ("line : " + line + "\t\tError format: fact character unvalid: " + line[j])
                return False
            j = j + 1
        j = 0
        while j < len(line):
            #REPRENDRE ICI
            j = j + 1
        self.rule_nb = self.rule_nb + 1
        return True
        pass

    def add_rule(self, line):
    #add the rule to stack
        pass

    def fact_is_ok(self, line, i):
    #fact after rules
    #only one fact-line
    #\n before and after line
        return True
        pass

    def add_facts(self, line):
    #add line to self.fact_line
        pass

    def queri_is_ok(self, line, i):
    #queri after rule and fact
    #only one queri-lines
    #\n before
        return True
        pass

    def add_queries(self, line):
    #add line to self.queri_line
        pass

    def parse(self):
        i = 0
        while i < len(self.lines):
            j = 0
            if self.lines[i] == '':
                pass
            elif self.lines[i][0] == '#':
                pass
            elif self.lines[i][0].isalpha():
                if self.rule_is_ok(self.lines[i], i):
                    self.add_rule(self.lines[i])
                else:
                    return False
            elif self.lines[i][0] == '=':
                if self.fact_is_ok(self.lines[i], i):
                    self.add_facts(self.lines[i])
                else:
                    return False
            elif self.lines[i][0] == '?':
                if self.queri_is_ok(self.lines[i], i):
                    self.add_queries(self.lines[i])
                else:
                    return False
            else:
                return False
            i = i + 1
        return True

def parse_entry(arg):
    if os.path.isfile(arg):
        if test_on == True:
            print ("Test le fichier suivant existe bien \n_______________\n" + arg + "\n_______________\n")
        fichier = File(arg)
        if fichier.parse():
            #proceed to treatment of information
            pass
        else:
            print("File " + arg + " not well formated.")
    else:
        print ("File " + arg + " not found")

def main(argv):
    for arg in argv:
        if test_on == True:
            print ("Test Reception des arguments \n_______________\n" + arg + "\n_______________\n")
        if arg.find('.txt') > 0:
            if test_on == True:
                print ("Test Recherche extension .txt = true pour \n_______________\n" + arg + "\n_______________\n")
            parse_entry(arg)
        else:
            print ("File " + arg + " not well formated. Please give .txt files only.")

if __name__ == "__main__":
    #ch = "ab@"
    #print(ch[2].isalpha())
    main(sys.argv[1:])
