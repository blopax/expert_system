import copy

import parsing
import node_utils
import graph


class Node:
    def __init__(self, content=None, children=None, depth=0, list_input=None, belong_to_graph=None):
        """
        Initialize a node either by filling each attribute or by giving a rule as a list_input format.
        :param str content: symbol (operator or fact: '|', '+', 'A', '<=>'...)
        :param int depth: give the depth of the node from root node.
        :param list children: list of Nodes that are linked to the Node
        :param list list_input: input as list. Can be valid rule or fact (eg: ['A'], ['A', '<=>', 'B'])
        """
        self.content = content
        self.depth = depth
        self.graph = belong_to_graph
        self.fact = None
        if not children:
            self.children = []
        else:
            self.children = children
        if list_input:
            self.fill_node(list_input)

    def fill_node(self, list_input):
        """
        Use input to fill content and children.
        :return: None
        """
        symbol, index = node_utils.find_symbol_to_treat(list_input)
        if symbol == '()':
            self.fill_node(list_input[1:-1])
            return
        self.content = symbol
        if symbol == '!':
            self.children.append(Node(list_input=list_input[index + 1:], depth=self.depth + 1))
        if symbol in parsing.BINARY_OPERATORS:
            self.children.append(Node(list_input=list_input[:index], depth=self.depth + 1))
            self.children.append(Node(list_input=list_input[index + 1:], depth=self.depth + 1))
        if symbol in parsing.ALLOWED_FACTS:
            self.children = []
            if self.graph:
                self.fact = self.graph.get_fact(symbol)
            if self.fact is None:
                self.fact = graph.Fact(symbol)

    def transform_graph_and_or_step(self, node):
        """
        Take a node and transform node and all depending nodes into a tree with only '+', '|' and '!'
        :param node:
        :return:
        """
        not_finished = False
        if node.content == '<=>':
            node_utils.transform_iff(node)
        elif node.content == '=>':
            node_utils.transform_imply(node)
        elif node.content == '^':
            node_utils.transform_xor(node)
        elif node.content == '!':
            child = node.children[0]
            if child.content not in parsing.ALLOWED_FACTS:
                tmp = node_utils.transform_not(child)
                node_utils.update_depth_node(tmp, -1)
                node_utils.update_node(node, content=child.content, depth=tmp.depth, children=tmp.children)
                del tmp
                not_finished = True
        for item in node.children:
            self.transform_graph_and_or(item)
        return not_finished

    def transform_graph_and_or(self, node):
        while self.transform_graph_and_or_step(node):
            pass

    @staticmethod
    def develop_and_or(node, position):
        """
        Develop a node that is a '|', and has a child that is a '+' into a node that is a '+'. And makes the
        necessary transformation on children (Development)
        :param node:
        :param position: position of the child that is a '+' on which development is performed
        :return:
        """
        node.content = '+'
        child0, child1 = node.children[0], node.children[1]
        if position == 0:
            node_utils.update_depth_node(child1, 1)
            new_child0 = Node(content='|', depth=node.depth + 1, children=[child0.children[0], child1])
            new_child1 = Node(content='|', depth=node.depth + 1,
                              children=[copy.deepcopy(child0.children[1]), copy.deepcopy(child1)])
        else:
            node_utils.update_depth_node(child0, 1)
            new_child0 = Node(content='|', depth=node.depth + 1,
                              children=[child0, child1.children[0]])
            new_child1 = Node(content='|', depth=node.depth + 1,
                              children=[copy.deepcopy(child0), copy.deepcopy(child1.children[1])])
        node.children = [new_child0, new_child1]

    @staticmethod
    def node_check_cnf(node):
        check = True
        for child in node.children:
            if node.content == '|' and child.content == '+':
                return False
            else:
                check = check & node.node_check_cnf(child)
        return check

    def transform_graph_cnf(self, node):
        """
        Take a node and transform node and all depending nodes into a tree that is a Conjuctive Normal Form
        :param node:
        :return:
        """
        if node.content == '|':
            if node.children[0].content == '+':
                self.develop_and_or(node, 0)
            elif node.children[1].content == '+':
                self.develop_and_or(node, 1)
        for item in node.children:
            self.transform_graph_cnf(item)
        while self.node_check_cnf(node) is False:
            self.transform_graph_cnf(node)

    def flatten_and_or(self, and_or):
        new_children = []
        for child in self.children:
            if child.content == and_or:
                for grandchild in child.children:
                    node_utils.update_depth_node(grandchild, -1)
                    new_children.append(grandchild)
            else:
                new_children.append(child)
            self.children = new_children
        while and_or in [item.content for item in self.children]:
            self.flatten_and_or(and_or)

    def flatten_graph_cnf(self):
        if self.content == '+':
            self.flatten_and_or('+')
        if self.content == '|':
            self.flatten_and_or('|')
        elif '|' in [child.content for child in self.children]:
            for child in self.children:
                child.flatten_and_or('|')


if __name__ == '__main__':
    rule = ['A', '=>', 'B', '<=>', '!', '(', '!', '!', 'C', '+', '!', '!', 'D', ')',
            '<=>', '(', 'A', '|', 'B', ')', '+', 'C', ')', '=>', 'C', '|', 'D']

    root = Node(list_input=rule)
    node_utils.show_graph(root)
    root.transform_graph_and_or(root)
    root.transform_graph_cnf(root)
    root.flatten_graph_cnf()
    node_utils.show_graph(root)
