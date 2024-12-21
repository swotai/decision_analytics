# %%
from enum import Enum
from typing import List, Optional, Dict, Tuple
from functools import reduce


class FunnelNodeType(Enum):
    INPUT = "input node"
    CALCULATED = "calculated node"


class CalculationType(Enum):
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"


class FunnelNode:
    def __init__(
        self, name: str, node_type: FunnelNodeType, value: Optional[float] = None
    ):
        self.name = name
        self.node_type = node_type
        self.value = value

    def __repr__(self):
        return (
            f"FunnelNode(name={self.name}, type={self.node_type}, value={self.value})"
        )


class Funnel:
    def __init__(self):
        self.nodes: Dict[str, FunnelNode] = {}

    def add_input(self, name: str, value: float):
        self.nodes[name] = FunnelNode(
            name=name, node_type=FunnelNodeType.INPUT, value=value
        )

    def get_node(self, name: str) -> FunnelNode:
        if name not in self.nodes:
            raise ValueError(f"Node '{name}' not found.")
        return self.nodes[name]

    def define_relationships(self, relationships: Dict[str, str]):
        for output, expression in relationships.items():
            self._process_relationship(output, expression)

    def _process_relationship(self, output: str, expression: str):
        tokens = expression.replace(" ", "").split("=")
        if len(tokens) != 2:
            raise ValueError(f"Invalid relationship: {expression}")
        _, formula = tokens
        inputs, operations = self._parse_expression(formula)
        result = self._evaluate(inputs, operations)

        self.nodes[output] = FunnelNode(
            name=output, node_type=FunnelNodeType.CALCULATED, value=result
        )

    def _parse_expression(self, formula: str) -> Tuple[List[FunnelNode], List[str]]:
        operations = []
        nodes = []
        current = ""
        for char in formula:
            if char in CalculationType._value2member_map_:
                if current:
                    nodes.append(self.get_node(current))
                    current = ""
                operations.append(char)
            else:
                current += char
        if current:
            nodes.append(self.get_node(current))
        return nodes, operations

    def _evaluate(self, nodes: List[FunnelNode], operations: List[str]) -> float:
        result = nodes[0].value
        if result is None:
            raise ValueError("Initial node value cannot be None.")
        for node, op in zip(nodes[1:], operations):
            if node.value is None:
                raise ValueError(f"Node '{node.name}' value is None.")
            if op == CalculationType.PLUS.value:
                result += node.value
            elif op == CalculationType.MINUS.value:
                result -= node.value
            elif op == CalculationType.MULTIPLY.value:
                result *= node.value
            elif op == CalculationType.DIVIDE.value:
                if node.value == 0:
                    raise ValueError("Cannot divide by zero.")
                result /= node.value
        return result

    def __repr__(self):
        return f"Funnel({self.nodes})"


# %%
# Sample Usage
funnel = Funnel()
funnel.add_input("total_users", 1000000)
funnel.add_input("subscribe_share", 0.2)
funnel.add_input("ctr", 0.01)
funnel.add_input("buy_rate", 0.005)

relationships = {
    "total_subscribers": "total_users * subscribe_share",
    "total_clicks": "total_subscribers * ctr",
    "total_buys": "total_clicks * buy_rate",
}

funnel.define_relationships(relationships)

print(f"Total Buys: {funnel.get_node('total_buys').value}")  # Outputs calculated value

# %%
