import logging
import re
import json

from decision_analytics import CalculatedNode, Node


class NodesCollection:
    """
    A funnel is a collection of nodes.
    """

    def __init__(self):
        self.nodes = {}

    def __iter__(self):
        return iter(self.nodes.values())

    def __repr__(self):
        input_nodes_count = len(self.get_input_nodes())
        calculated_nodes_count = len(self.get_calculated_nodes())
        return (
            f"NodesCollection with {len(self.nodes)} nodes: "
            f"{input_nodes_count} input nodes and {calculated_nodes_count} calculated nodes."
        )

    def to_json_str(self) -> str:
        """
        Serializes all nodes in the collection to a JSON string.

        Returns
        -------
        str
            JSON string representation of all nodes
        """
        nodes_data = []
        for node in self.nodes.values():
            node_dict = {
                "name": node.name,
                "format_str": node.format_str,
                "node_type": node.node_type,
                "value_low": node.value_low,
                "value_mid": node.value_mid,
                "value_high": node.value_high,
                "long_name": node.long_name,
                "description": node.description,
                "value": node.value,
                "is_kpi": node.is_kpi,
                "readable_large_number": node.readable_large_number,
            }
            if isinstance(node, CalculatedNode):
                node_dict["definition"] = node.definition
            nodes_data.append(node_dict)
        return json.dumps(nodes_data)

    def from_json_str(self, json_str: str) -> None:
        """
        Sets up all nodes from a JSON string, overwriting any existing nodes.

        Parameters
        ----------
        json_str : str
            JSON string containing node definitions

        Raises
        ------
        ValueError
            If the JSON string is invalid or missing required node properties
        """
        try:
            nodes_data = json.loads(json_str)
            if not isinstance(nodes_data, list):
                raise ValueError("JSON must contain a list of node definitions")

            # Clear existing nodes
            self.nodes = {}

            # Add nodes from JSON
            self.add_nodes(nodes_data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {str(e)}")

    def add_nodes(self, nodes_list: list):
        """Add nodes
        This method is used for loading nodes from json as well as just manually adding nodes one by one.

        Parameters
        ----------
        nodes_list : list
            List of dictionaries each specifying one node. Can be either input or calculated node.
        """
        for node in nodes_list:
            if node["node_type"] == "input":
                self.nodes[node["name"]] = Node(**node)
            elif node["node_type"] == "calculation":
                self.nodes[node["name"]] = CalculatedNode(**node)
            else:
                raise ValueError(
                    f'Node must be either "input" or "calculation". Bad node definition: {node}'
                )

        self._check_valid_definitions()
        self._rank_nodes()

    def remove_node(self, node_name: str) -> None:
        """
        Remove a node from the collection.
        """
        logging.debug(f"Removing node: {node_name}")
        del self.nodes[node_name]

    def set_node_values_from_dict(self, values_dict: dict, lookup: bool = True) -> None:
        """
        Set the values of nodes from a dictionary. If lookup is True, it will look up the value from value_percentiles in the collection and set it to the node.
        Otherwise, it will directly set the value to the node. This method is used in simulationg to set values dynamically

        Parameters
        ----------
        values_dict : dict
            Dictionary, with the input node name as key, and the desired value as value.
            If using lookup, value should be one of [0,1,2]
        lookup : bool, optional
            Whether to lookup actual value of node from value_percentiles, by default True

        Raises
        ------
        ValueError
            If node does not exist
        ValueError
            If user tries to set value of a calculated node
        ValueError
            If the value provided is not a number (int/float)
        ValueError
            If the value provided is not a number (int/float)
        ValueError
            If the node doesn't have a 'value' attribute (this should be impossible)
        """
        for node_name, value in values_dict.items():
            try:
                node = self.get_node(node_name)
                if node is None:
                    raise ValueError(f"Node '{node_name}' does not exist.")
                if isinstance(node, CalculatedNode):
                    raise ValueError(
                        f"Cannot set value for calculated node '{node_name}'."
                    )
                if not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Value '{value}' is not a valid number for node '{node_name}'."
                    )

                if lookup:
                    # Only do lookup if value percentiles exist. Otherwise don't update the value
                    if all([node.value_low, node.value_mid, node.value_high]):
                        # Ensure value is an integer index for the percentiles
                        if not isinstance(value, int) or value not in [0, 1, 2]:
                            raise ValueError(
                                f"When using lookup, value must be 0, 1, or 2 for 10th, 50th, or 90th percentile. Got {value}"
                            )
                        if value == 0:
                            v = node.value_low
                        elif value == 1:
                            v = node.value_mid
                        else:
                            v = node.value_high
                    else:
                        v = node.value
                else:
                    v = value
                node.value = v
            except KeyError:
                raise ValueError(
                    f"Value '{value}' is not a valid value for node '{node_name}'."
                )
            except AttributeError:
                raise ValueError(
                    f"Node '{node_name}' does not have a 'value' attribute."
                )

    def get_node(self, name: str) -> Node:
        """
        Get a node by its name.

        Parameters
        ----------
        name : str
            Name of the node

        Returns
        -------
        Node
            Reference to the node object

        Raises
        ------
        ValueError
            If user provided a name that doesn't exists in the collection.
        """
        for node in self.nodes:
            if node == name:
                return self.nodes[node]
        raise ValueError(f"Node '{name}' does not exist.")

    def get_input_nodes(self):
        return [
            node for node in self.nodes.values() if not isinstance(node, CalculatedNode)
        ]

    def get_calculated_nodes(self):
        return [
            node for node in self.nodes.values() if isinstance(node, CalculatedNode)
        ]

    def get_kpi_nodes(self):
        return [node for node in self.nodes.values() if node.is_kpi]

    def get_unused_nodes(self) -> list:
        """Get a list of input nodes that are not included in any calculated node definitions"""
        used_node_names = set()
        for node in self.nodes.values():
            if isinstance(node, CalculatedNode):
                used_node_names.update(re.findall(r"\b\w+\b", node.definition))
        return [
            node for node in self.get_input_nodes() if node.name not in used_node_names
        ]

    def get_nodes_mapping(self) -> dict:
        """Get a dict where each key is each node's name and value is its corresponding long name"""
        return {node.name: node.long_name for node in self.nodes.values()}

    def _check_valid_definitions(self):
        """Make sure that the definition of the relationship is valid and is safe."""
        allowed_operators = set("+-*/() _0123456789")  # Allowing digits now
        for node in self.nodes.values():
            if isinstance(node, CalculatedNode):
                # Extract all variable names from the definition
                variables = re.findall(r"\b\w+\b", node.definition)
                for var in variables:
                    # Accept digit as valid
                    if var not in self.nodes and not var.isdigit():
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

        # All input nodes get rank 0
        for node in input_nodes:
            node.rank = 0

        # Rank the calculated nodes
        rank = 1
        max_iterations = len(calculated_nodes)  # Prevent infinite loops
        iteration_count = 0

        while calculated_nodes and iteration_count < max_iterations:
            iteration_count += 1
            for node in calculated_nodes[:]:
                variables = re.findall(r"\b\w+\b", node.definition)
                # Check if all variables are resolved and ranked
                # Allow constants in the definition
                if all(
                    var.isdigit() or (var in self.nodes and self.nodes[var].rank < rank)
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

    def refresh_nodes(self):
        """
        Re-evaluates and updates the values of all nodes in the collection,
        especially calculated nodes, based on their dependencies.

        This method performs the following steps:
        1. Re-ranks all nodes to ensure correct evaluation order based on dependencies.
        2. Iterates through the ranked nodes and, for each CalculatedNode,
           safely evaluates its definition using the current values of its
           dependent nodes.
        3. Logs warnings if no calculated node is designated as a Key Performance Indicator (KPI).
        """
        self._rank_nodes()
        ordered_list = [node for node in self.nodes]
        logging.debug(f"Ordered list: {ordered_list}")

        if not any(node.is_kpi for node in self.nodes.values()):
            logging.warning("No calculated node designated in the nodes collection.")

        for item in ordered_list:
            node = self.nodes[item]
            if isinstance(node, CalculatedNode):
                import ast

                # Create a safe dictionary of variables, add `__builtins__` for constants
                safe_dict = {
                    var: self.nodes[var].value
                    for var in re.findall(r"\b\w+\b", node.definition)
                    if var in self.nodes and self.nodes[var].value is not None
                }

                # Parse the definition into an AST node
                node_ast = ast.parse(node.definition, mode="eval")

                # Define a safe eval function
                def safe_eval(node_ast, safe_dict):
                    try:
                        logging.debug(
                            f"Evaluating AST: {ast.dump(node_ast)} with safe_dict: {safe_dict}"
                        )
                        code = compile(node_ast, "<string>", "eval")
                        result = eval(
                            code,
                            {"__builtins__": None},
                            {**safe_dict, **{"__builtins__": None}},
                        )
                        logging.debug(f"Result of evaluation: {result}")
                        return result
                    except Exception as e:
                        logging.error(f"Error during safe_eval: {e}")
                        raise

                # Evaluate the node definition safely
                node.update_value(safe_eval(node_ast, safe_dict))

    def reset_input_nodes(self):
        # STILL DOESN'T WORK
        """
        Reset all input nodes to their median value.

        If value_percentiles is available, use the 50th percentile (median).
        If no percentiles are defined, set value to None.
        """
        for node in self.nodes.values():
            # Check if the node is an input node
            if node.node_type is not None:
                # If value percentiles are defined and is a 3 element tuple, use the median (50th percentile)
                if all([node.value_low, node.value_mid, node.value_high]):
                    try:
                        node.value = node.value_mid
                    except (IndexError, TypeError):
                        # If percentiles can't be processed, set to None
                        node.value = None
                else:
                    # If no percentiles, don't update (this might be a constant node)
                    # node.value = None
                    pass

        # Refresh nodes after resetting
        self.refresh_nodes()
