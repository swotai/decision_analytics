import re
from typing import Optional

from .utils import format_float


class Node:

    def __init__(
        self,
        name: str,
        format_str: str,
        input_type: str,
        value: Optional[float] = None,
        readable_large_number: bool = True,
    ):
        if input_type == "input" and value is None:
            raise ValueError("Value must be provided when input_type is 'input'")

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
        if self.value is not None:
            return format_float(self.value, self.format_str, self.readable_large_number)
        else:
            return "N/A"

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.input_type}, Value:{self.pretty_value()}, Rank: {self.rank})"
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
        node_description = f"{self.name} (Type: {self.input_type}, Definition: {self.definition}, Value:{self.pretty_value()}, Rank: {self.rank})"
        return node_description


class NodesCollection:
    """
    A funnel is a nodes collection
    """

    def __init__(self):
        self.nodes = {}

    def add_nodes(self, nodes_list: list):
        """Add nodes
        This method is used for loading nodes from json as well as just manually adding nodes one by one.

        Parameters
        ----------
        nodes_list : list
            List of dictionaries each specifying one node. Can be either input or calculated node.
        """
        for node in nodes_list:
            if "definition" in node.keys():
                self.nodes[node["name"]] = CalculatedNode(**node)
            else:
                self.nodes[node["name"]] = Node(**node)
        self.check_valid_definitions()
        self.rank_nodes()

    def remove_node(self, node_name: str):
        del self.nodes[node_name]

    def get_node(self, name: str) -> Optional[Node]:
        for node in self.nodes:
            if node == name:
                return self.nodes[node]
        return None

    def check_valid_definitions(self):
        """Make sure that the definition of the relationship is valid and is safe"""

        allowed_operators = set("+-*/() _")
        for node in self.nodes.values():
            if isinstance(node, CalculatedNode):
                # Extract all variable names from the definition
                variables = re.findall(r"\b\w+\b", node.definition)
                for var in variables:
                    if var not in self.nodes:
                        raise ValueError(
                            f"Variable '{var}' in node '{node.name}' is not a valid input node."
                        )
                # Check for invalid characters in the definition
                for char in node.definition:
                    if not char.isalnum() and char not in allowed_operators:
                        raise ValueError(
                            f"Invalid character '{char}' in definition of node '{node.name}'."
                        )

    def rank_nodes(self):
        # Get list of all input nodes, no need to rank them.
        input_nodes = [
            node for node in self.nodes.values() if not isinstance(node, CalculatedNode)
        ]

        # Get list of all calculated nodes
        calculated_nodes = [
            node for node in self.nodes.values() if isinstance(node, CalculatedNode)
        ]

        # all input nodes get rank 0
        for node in input_nodes:
            node.rank = 0

        # rank the calculated nodes
        rank = 1
        max_iterations = len(calculated_nodes)  # Prevent infinite loops
        iteration_count = 0

        while calculated_nodes and iteration_count < max_iterations:
            iteration_count += 1
            for node in calculated_nodes[:]:
                variables = re.findall(r"\b\w+\b", node.definition)
                # Check if all variables are resolved and ranked
                if all(
                    var in self.nodes and self.nodes[var].rank < rank
                    for var in variables
                ):
                    node.rank = rank
                    calculated_nodes.remove(node)

            rank += 1

        # Check if there are unranked nodes remaining
        if calculated_nodes:
            error_message = (
                "Unresolvable dependencies detected for the following nodes:\n"
            )
            error_message += "\n".join(
                f"{node.name} : {node.definition}" for node in calculated_nodes
            )
            raise ValueError(error_message)

        # Sorting the nodes dictionary by the rank attribute of the node objects
        self.nodes = dict(sorted(self.nodes.items(), key=lambda item: item[1].rank))

    def update_values(self):
        self.rank_nodes()
        ordered_list = [node for node in self.nodes]
        print("ordered list:", ordered_list)
        for item in ordered_list:
            node = self.nodes[item]
            if isinstance(node, CalculatedNode):
                import ast

                # Create a safe dictionary of variables
                safe_dict = {
                    var: self.nodes[var].value
                    for var in re.findall(r"\b\w+\b", node.definition)
                    if self.nodes[var].value is not None
                }

                # Parse the definition into an AST node
                node_ast = ast.parse(node.definition, mode="eval")

                # Define a safe eval function
                def safe_eval(node_ast, safe_dict):
                    code = compile(node_ast, "<string>", "eval")
                    print("===========================")
                    print("processing:", node.name)
                    print(node.definition)
                    print(node_ast)
                    print(code)
                    print(safe_dict)
                    print("===========================")
                    return eval(code, {"__builtins__": None}, safe_dict)

                # Evaluate the node definition safely
                node.value = safe_eval(node_ast, safe_dict)

    def __repr__(self):
        return f"NodesCollection with {len(self.nodes)} nodes."
