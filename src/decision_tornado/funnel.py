import re
from typing import Optional

from .utils import format_float


class Node:
    def __init__(
        self,
        name: str,
        format_str: str,
        input_type: str,
        value_percentiles: Optional[tuple] = None,
        long_name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[float] = None,
        readable_large_number: bool = True,
    ):
        """Initializes a node object

        Parameters
        ----------
        name : str
            The name of the node.
        format_str : str
            The format string for the node's value. For example, ".2%" for percentage values.
            If left blank, large numbers will be converted to readable format with K/M/B/T.
        input_type : str
            The type of input for the node, should be either "input" or "calculation".
        value_percentiles : Optional[tuple], optional
            The tuple of values for the node at the 10th, 50th, and 90th percentiles. By default None.
        long_name : Optional[str], optional
            A longer, more descriptive name for the node, by default None.
            If left blank, will convert regular_name to Regular Name.
        description : Optional[str], optional
            A brief description of the node, by default None.
        value : Optional[float], optional
            The initial value of the node, by default None.
        readable_large_number : bool, optional
            Whether to format large numbers in a more readable way, by default True.

        Raises
        ------
        ValueError
            If input_type is 'input' and value is None.
        ValueError
            If input_type is not 'input' or 'calculation'.
        ValueError
            If value_percentiles is provided and does not contain exactly 3 values.
        """
        # Check for invalid inputs
        if input_type == "input" and value is None:
            raise ValueError("Value must be provided when input_type is 'input'")
        if input_type not in ["input", "calculation"]:
            raise ValueError("input_type must be either 'input' or 'calculation'")

        # metadata attributes
        self.name = name
        self.input_type = input_type
        self.readable_large_number = readable_large_number
        self.long_name = name if long_name is None else long_name
        self.description = description

        # value and distribution attributes
        self.value = value
        self.format_str = format_str
        if value_percentiles is not None and len(value_percentiles) != 3:
            raise ValueError(
                "Range must contain exactly 3 values representing 10th, 50th, and 90th percentiles"
            )
        self.value_percentiles = value_percentiles

        # rank, for sorting nodes
        self.rank = 0

    def _pretty_value(self):
        """
        Pretty printing the value of the node, applying string formatting to the numeric value
        """
        if self.value is not None:
            return format_float(self.value, self.format_str, self.readable_large_number)
        else:
            return "N/A"

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.input_type}, Value:{self._pretty_value()}, Rank: {self.rank})"
        return node_description

    def get_chart_str(self):
        node_description = f"{self.long_name}\n{self._pretty_value()}"
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
        node_description = f"{self.name} (Type: {self.input_type}, Definition: {self.definition}, Value:{self._pretty_value()}, Rank: {self.rank})"
        return node_description


class NodesCollection:
    """
    A funnel is a collection of nodes.
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
        self._check_valid_definitions()
        self._rank_nodes()

    def remove_node(self, node_name: str):
        del self.nodes[node_name]

    def get_node(self, name: str) -> Optional[Node]:
        for node in self.nodes:
            if node == name:
                return self.nodes[node]
        return None

    def get_input_nodes(self):
        return [
            node for node in self.nodes.values() if not isinstance(node, CalculatedNode)
        ]

    def get_calculated_nodes(self):
        return [
            node for node in self.nodes.values() if isinstance(node, CalculatedNode)
        ]

    def get_unused_nodes(self):
        """Get a list of nodes that is not included in any calculated node definitions"""
        used_nodes = set()
        for node in self.nodes.values():
            if isinstance(node, CalculatedNode):
                used_nodes.update(re.findall(r"\b\w+\b", node.definition))
        return [node for node in self.nodes.values() if node.name not in used_nodes]

    def _check_valid_definitions(self):
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

    def _rank_nodes(self):
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
        self._rank_nodes()
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
                    return eval(code, {"__builtins__": None}, safe_dict)

                # Evaluate the node definition safely
                node.value = safe_eval(node_ast, safe_dict)

    def __repr__(self):
        return f"NodesCollection with {len(self.nodes)} nodes."
