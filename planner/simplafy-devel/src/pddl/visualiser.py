from collections import namedtuple
import json
import math

from pddl.state import applicable
from pddl.action import Action
from pddl.pddl_preprocessor import compute_all_facts

Node = namedtuple('Node', ['f_value', 'state', 'h_value', 'parent'])


class Visualiser:
    """A visualiser class to generate JSON suitable for the Statespace Heuristic view:
    https://github.com/AI-Planning/statespace
    That is used in https://editor.planning.domains/
    """

    def __init__(self, action_space: list[Action], goal: tuple[frozenset, frozenset]):
        self.root: Node = None
        self.tree: dict[Node, list] = dict()
        self.node_number: dict[Node, int] = dict()
        self.node_index = 0
        all_facts = compute_all_facts(action_space)
        self.fact_vector = []
        self.fact_index = dict()
        self.goal = goal
        for index, fact in enumerate(all_facts):
            self.fact_vector.append(fact)
            self.fact_index[fact] = index

    def state_to_hex(self, state: frozenset[tuple]) -> str:
        _bin = ['0'] * len(self.fact_vector)
        for fact in state:
            if fact not in self.fact_index:  # Nasty special case for our algorithm
                print("Missing fact %s" % fact)
            else:
                _bin[self.fact_index[fact]] = '1'
        _hex = hex(int(str("".join(_bin)), 2))
        return _hex

    def node_to_color(self, node: Node) -> str:
        if applicable(node.state, self.goal[0], self.goal[1]):
            return "#FF0000"
        else:
            if math.isinf(node.h_value):
                return "#00FFFF"
            else:
                return '#0000'+hex(255 - int(node.h_value))[2:]

    def add_node(self, parent_node: Node, child_node: Node):
        if parent_node:
            parent_node = Node(*parent_node)
        child_node = Node(*child_node)
        if self.root is None:
            self.root = child_node
        else:
            if parent_node not in self.tree:
                self.tree[parent_node] = []
            self.tree[parent_node].append(child_node)
        if child_node not in self.node_number:
            self.node_number[child_node] = self.node_index
            self.node_index += 1

    def json_dict_children(self, node: Node) -> dict:
        if node in self.tree:
            children = [self.json_dict_children(child) for child in self.tree[node]]
        else:
            children = []
        state_hex = self.state_to_hex(node.state)
        color = self.node_to_color(node)
        name = "state %d" % self.node_number[node]
        action = repr(node.parent[0])
        json_node = {"name": name, "color": color, "state": state_hex, "children": children, "action": action}
        return json_node

    def get_json_string(self):
        json_dict = [self.json_dict_children(child) for child in self.tree[self.root]]
        state_hex = self.state_to_hex(self.root.state)
        predicates = self.fact_vector
        json_string = {"name": "initial_state", "color": "#0000FF", "state": state_hex, "children": json_dict, "predicates": predicates}
        return json.dumps(json_string)
