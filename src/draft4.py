from utils import format_float


class Node:
    def __init__(
        self,
        name: str,
        value: float,
        format_str: str,
        input_type: str,
        readable_large_number: bool = True,
    ):
        self.name = name
        self.value = value
        self.format_str = format_str
        self.input_type = input_type
        self.readable_large_number = readable_large_number
        self.rank = 0

    def pretty_value(self):
        """
        Pretty printing the value of the node, applying string formatting to the numeric value
        """
        return format_float(self.value, self.format_str, self.readable_large_number)

    def __repr__(self):
        node_description = (
            f"{self.name} (Type: {self.input_type}, Value:{self.pretty_value()})"
        )
        return node_description


class CalculatedNode(Node):
    def __init__(self, definition: str, **kwargs):
        self.definition = definition
        # pass rest to node init
        super().__init__(**kwargs)

        assert (
            self.input_type == "calculation"
        ), "Relation node must be calculation type"
        self.rank = 1

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.input_type}, Definition: {self.definition}, Value:{self.pretty_value()})"
        return node_description


class NodesCollection:
    def __init__(self):
        self.nodes = {}

    def add_nodes(self, nodes_list: list):
        for node in nodes_list:
            if "definition" in node.keys():
                self.nodes[node.name] = CalculatedNode(**node)
            else:
                self.nodes[node.name] = Node(**node)

    def remove_node(self, node_name: str):
        del self.nodes[node_name]

    def get_node(self, name: str) -> Node:
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    def rank_nodes(self):
        # Get list of all input nodes
        # Get list of all calculated nodes
        # subset list of calculated nodes where inputs are input nodes, rank 1
        # subset list of calculated nodes where inputs are input nodes + rank 1 nodes, rank +=1
        # repeat till all calculated noes covered
        pass

    def sort_nodes(self):
        # Sorting the dictionary by the rank attribute of the node objects
        self.nodes = dict(sorted(self.nodes.items(), key=lambda item: item[1].rank))

    def __repr__(self):
        return f"NodesCollection with {len(self.nodes)} nodes."


class Funnel:
    def __init__(self):
        self.nodes = []

    def check_valid_definition(self):
        """Make sure that the definition of the relationship is valid and is safe"""
        # This can't happen inside calculated node, it has to happen inside the collection instead, as it needs to know the collection of input and calculated nodes.
        # Check to make sure all vars are valid input nodes (meaning this needs to be done after all nodes are finish init)
        # Check to make sure only allowed operators (+ - * / and () only )

    def sort_calculated_nodes(self):
        """
        Sort calculated nodes by level of dependency
        - go through list of all nodes, rank in order of:
            - input nodes
            - calculated nodes with all input nodes present
        - repeat till all nodes covered
        """

    def update_values(self):
        # This also needs to be in the collection class as it needs input from other node values
        self.value = safe_eval()
