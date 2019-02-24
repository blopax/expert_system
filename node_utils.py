import parser
# rom node import Node


def find_symbol_to_treat(list_input):
    """
    Parse the input to define the least priority symbol and its index (if several candidates, take the last one)
    :param list list_input:
    :return: str symbol, int index
    """
    no_parenthesis_input = clean_parenthesis(list_input)
    index, symbol = 0, None
    if set(no_parenthesis_input) == {None}:
        symbol = '()'  # voir si accepte max si n existe pas
    elif '<=>' in no_parenthesis_input:
        symbol = '<=>'
    elif '=>' in no_parenthesis_input:
        symbol = '=>'
    elif '^' in no_parenthesis_input:
        symbol = '^'
    elif '|' in no_parenthesis_input:
        symbol = "|"
    elif '+' in no_parenthesis_input:
        symbol = '+'
    elif '!' in no_parenthesis_input:
        symbol = '!'
    elif len(list_input) > 0 and list_input[0] in parser.ALLOWED_FACTS:
        symbol = list_input[0]
    if symbol in parser.BINARY_OPERATORS:
        symbol_loc = [loc for loc, val in enumerate(no_parenthesis_input) if val == symbol]
        if symbol_loc:
            index = symbol_loc[-1]
    else:
        index = 0
    return symbol, index


# voir si raise exception

def clean_parenthesis(list_input):
    """
    Replace parenthesis and everything between matching parenthesis by None
    :param list_input:
    :return: list
    """
    clean_input = []
    in_parenthesis = 0
    for item in list_input:
        if item == '(':
            in_parenthesis += 1
        if item == ')':
            in_parenthesis -= 1
        if in_parenthesis > 0 or item in '()':
            clean_input.append(None)
        else:
            clean_input.append(item)
    return clean_input


def update_vertical_lines(vertical_lines, mode=None, children=None, depth=0):
    if mode == 'append':
        while len(vertical_lines) < depth:
            vertical_lines.append(0)
        if len(vertical_lines) == depth:
            vertical_lines.append(len(children))
    elif mode == 'pop':
        while len(vertical_lines) > 1 and vertical_lines[-1] == 0:
            vertical_lines.pop()
    elif mode == 'print':
        for item in vertical_lines:
            if item > 0:
                print('¥     ', end='')
            else:
                print('      ', end='')
        print()
    return vertical_lines


def show_graph(node, vertical_lines=None):
    """
    Display node and all dependent nodes.
    :param Node node: node that will be displayed (with its descendants
    :param dict vertical_lines: count number of children when 2 are expected
    :return:
    """
    if vertical_lines is None:
        vertical_lines = []
    for i in range(node.depth):
        if i == node.depth - 1:
            print('¥_____', end='')
            if vertical_lines:
                vertical_lines[-1] -= 1
        elif vertical_lines and vertical_lines[i] > 0:
            print('¥     ', end='')
        else:
            print('      ', end='')
    print(node.content, node.depth)
    vertical_lines = update_vertical_lines(vertical_lines, mode='pop')
    if not node.children:
        update_vertical_lines(vertical_lines, mode='print')
    for nb, child in enumerate(node.children):
        vertical_lines = update_vertical_lines(vertical_lines, mode='append',
                                               children=node.children, depth=node.depth)
        show_graph(child, vertical_lines)


#changer nom en show node_tree

def copy_node(node):  # replace par deep copy ?
    node_copy = Node()
    node_copy.content = node.content
    node_copy.depth = node.depth
    node_copy.children = []
    for item in node.children:
        node_copy.children.append(copy_node(item))
    return node_copy


def update_node(node, content=None, depth=None, children=None):
    if content:
        node.content = content
    if depth:
        node.depth = depth
    if children is not None:
        node.children = children


def update_depth_node(node, depth_delta):
    node.depth += depth_delta
    for item in node.children:
        update_depth_node(item, depth_delta)

def transform_iff(node):
    """
    Called when node.content == "<=>". Returns a node that has the same meaning with '|', '+' and '!'
    :param node: has to be '<=>'
    :return: node:
    """
    if node.content == "<=>":
        child0, child1 = node.children[0], node.children[1]
        update_depth_node(child0, 1)
        update_depth_node(child1, 1)
        ch0 = Node(content='|', children=[child0, transform_not(copy_node(child1))], depth=node.depth + 1)
        ch1 = Node(content='|', children=[transform_not(copy_node(child0)), child1], depth=node.depth + 1)
        update_node(node, content='+', children=[ch0, ch1])
    return node


def transform_imply(node):
    """
    Called when node.content == "=>". Returns a node that has the same meaning with '|', '+' and '!'
    :param node: has to be '=>'
    :return: node:
    """
    if node.content == "=>":
        child0, child1 = node.children[0], node.children[1]
        update_node(node, content='|', children=[transform_not(child0), child1])
    return node


def transform_xor(node):
    """
    Called when node.content == "^". Returns a node that has the same meaning with '|', '+' and '!'
    :param node: has to be '^'
    :return: node:
    """
    if node.content == "^":
        child0, child1 = node.children[0], node.children[1]
        update_depth_node(child0, 1)
        update_depth_node(child1, 1)
        new_child0 = Node(content='|', children=[child0, child1], depth=node.depth + 1)
        new_child1 = Node(content='|', children=[transform_not(copy_node(child0)),
                                                 transform_not(copy_node(child1))], depth=node.depth + 1)
        update_node(node, content='+', children=[new_child0, new_child1])
    return node


def not_not(node):
    """
    Called when node.content == "!". Returns a node that has the same meaning ('!!' is positive)
    :param node: has to be '!'
    :return: node:
    """
    if node.content == "!":
        child0 = node.children[0]
        update_depth_node(child0, -1)
        update_node(node, content=child0.content, depth=child0.depth, children=child0.children)
        del child0
    return node


def not__imply_or_and(node, new, both_children_not=True):
    """
    Return a node that is the result of not(node).
    :param node: content can be '=>', '|' or '+'
    :param new: is the new_content of the node (so '+' if node.content == '|' or '=>' and '|' if not
    :param both_children_not: Has to be true if node.content is '|' or '+' and False otherwise
    :return:
    """
    child0, child1 = node.children[0], node.children[1]
    if both_children_not:
        update_node(node, content=new, children=[transform_not(child0), transform_not(child1)])
    else:
        update_node(node, content=new, children=[child0, transform_not(child1)])
    return node


def not_fact(node):
    """
    Called when node.content is a fact. Returns a node that is '!' and has the fact for a child
    :param node: has to be a fact
    :return: node:
    """
    child = copy_node(node)
    update_depth_node(child, +1)
    update_node(node, content='!', children=[child])
    return node


def transform_not(node):
    """
    Returns the negation of a node.
    """
    if node.content == '!':
        node = not_not(node)
    elif node.content == '<=>':
        node.content = '^'
    elif node.content == '=>':
        node = not__imply_or_and(node, '+', False)
    elif node.content == '^':
        node.content = '<=>'
    elif node.content == '|':
        node = not__imply_or_and(node, '+', True)
    elif node.content == '+':
        node = not__imply_or_and(node, '|', True)
    elif node.content in parser.ALLOWED_FACTS:
        node = not_fact(node)
    return node
