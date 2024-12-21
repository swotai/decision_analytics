# %%
from enum import Enum
from typing import List, Optional


class FunnelNodeType(Enum):
    INPUT = "input node"
    CALCULATED = "calculated node"


class CalculationType(Enum):
    # If multiple input, it'll simply repeat for each input
    # input ordering matters!!
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "×"
    DIVIDE = "÷"


class FunnelNode:
    def __init__(
        self,
        name: str,
        node_type: FunnelNodeType,
        value: Optional[float] = None,
        format_str: Optional[str] = None,
    ) -> None:
        self.name = name
        self.value = value
        self.format_str = format_str
        self.node_type = node_type


# %%
class NodeRelationship:
    def __init__(
        self,
        input_nodes: List[FunnelNode],
        output_node: FunnelNode,
        operation: CalculationType,
    ):
        self.input_nodes = input_nodes
        self.output_node = output_node
        self.operation = operation

    def calculate(self):
        if self.operation == CalculationType.PLUS:
            result = 0
            for node in self.input_nodes:
                if node.value is not None:
                    result += node.value
        elif self.operation == CalculationType.MINUS:
            result = 0
            for node in self.input_nodes:
                if node.value is not None:
                    result -= node.value
        elif self.operation == CalculationType.MULTIPLY:
            result = 1
            for node in self.input_nodes:
                if node.value is not None:
                    result *= node.value
        elif self.operation == CalculationType.DIVIDE:
            result = 1
            for node in self.input_nodes:
                if node.value is not None and node.value != 0:
                    result /= node.value
                else:
                    raise ValueError("Cannot divide by zero!")
        self.output_node.value = result


# %%
class Funnel:
    def __init__(self):
        self.nodes: List[FunnelNode] = []

    def add_node(self, node: FunnelNode):
        self.nodes.append(node)

    def get_node(self, name: str) -> Optional[FunnelNode]:
        """Retrieve a FunnelNode by its description (name)."""
        for node in self.nodes:
            if node.name == name:
                return node
        return None  # Return None if no matching node is found

    def get_all_nodes_name_in_list(self) -> List[str]:
        """Return a list of names of all FunnelNodes."""
        return [node.name for node in self.nodes]

    def calculate_nodes(self):
        pass

    def __repr__(self):
        node_descriptions = ", ".join(
            f"{node.name} (Type: {node.node_type}, Value: {node.value})"
            for node in self.nodes
        )
        return f"Funnel(Nodes: [{node_descriptions}])"


# %%

# Sample usage:
quantity_node = FunnelNode(name="Quantity", node_type=FunnelNodeType.INPUT, value=10.0)
price_node = FunnelNode(name="Price", node_type=FunnelNodeType.INPUT, value=15.0)
revenue_node = FunnelNode(name="Revenue", node_type=FunnelNodeType.CALCULATED)

relationship = NodeRelationship(
    input_nodes=[price_node, quantity_node],
    output_node=revenue_node,
    operation=CalculationType.MULTIPLY,
)

# Perform the calculation
relationship.calculate()

print(revenue_node.value)  # Outputs: 150.0 (10.0 * 15.0)

# %%
# How i want to specify input nodes and relationships?

inputs = {"Total users", "subscribe share", "ctr", "buy rate"}

relationships = {
    "total subscribers = total users * subscribe share",
    "total clicks = total subscribers * ctr",
    "total buys = total clicks * buy rate",
}


#%%
```python main.py
# ... existing code ...
class Funnel:
    def __init__(self):
        self.nodes: List[FunnelNode] = []
        self.relationships: List[NodeRelationship] = []

    def add_input(self, name: str, value: float):
        node = FunnelNode(name=name, node_type=FunnelNodeType.INPUT, value=value)
        self.add_node(node)

    def define_relationships(self, relationships: dict):
        for output, expression in relationships.items():
            output_node = self.get_node(output)
            if output_node is None:
                output_node = FunnelNode(name=output, node_type=FunnelNodeType.CALCULATED)
                self.add_node(output_node)
            
            inputs = self.parse_expression(expression)
            relationship = NodeRelationship(input_nodes=inputs, output_node=output_node, operation=self.infer_operation(expression))
            self.relationships.append(relationship)

    def parse_expression(self, expression: str) -> List[FunnelNode]:
        # Assume a simple parser for this example
        input_names = [name.strip() for name in expression.split('=')[1].split('*') if name.strip()]
        return [self.get_node(name) for name in input_names]

    def infer_operation(self, expression: str) -> CalculationType:
        if '*' in expression:
            return CalculationType.MULTIPLY
        # Add logic for different operations if needed
        return CalculationType.PLUS  # Default fallback

# Sample usage:
funnel = Funnel()
funnel.add_input("Total users", 100)
funnel.add_input("subscribe share", 0.5)
funnel.add_input("ctr", 0.2)
funnel.add_input("buy rate", 0.1)

relationships = {
    "total subscribers": "total users * subscribe share",
    "total clicks": "total subscribers * ctr",
    "total buys": "total clicks * buy rate",
}

funnel.define_relationships(relationships)

for relationship in funnel.relationships:
    relationship.calculate()

print(funnel.get_node("total buys").value)  # Outputs the calculated value
# ...
```

#%%
```python main.py
# ... existing code ...

class Funnel:
    # ... existing code ...

    def parse_expression(self, expression: str) -> List[FunnelNode]:
        operations = {
            '+': CalculationType.PLUS,
            '-': CalculationType.MINUS,
            '*': CalculationType.MULTIPLY,
            '/': CalculationType.DIVIDE
        }
        
        terms = [term.strip() for term in expression.split('=')[1].split()]
        input_nodes = []
        current_operation = None

        for term in terms:
            if term in operations:
                current_operation = operations[term]
            else:
                node = self.get_node(term)
                if node is None:
                    node = FunnelNode(name=term, node_type=FunnelNodeType.CALCULATED)
                    self.add_node(node)
                input_nodes.append((node, current_operation))
        
        return input_nodes

    def define_relationships(self, relationships: dict):
        for output, expression in relationships.items():
            output_node = self.get_node(output)
            if output_node is None:
                output_node = FunnelNode(name=output, node_type=FunnelNodeType.CALCULATED)
                self.add_node(output_node)

            input_terms = self.parse_expression(expression)
            current_result = input_terms[0][0].value if input_terms[0][0].value is not None else 0

            for node, operation in input_terms[1:]:
                if node.value is not None:
                    if operation == CalculationType.PLUS:
                        current_result += node.value
                    elif operation == CalculationType.MINUS:
                        current_result -= node.value
                    elif operation == CalculationType.MULTIPLY:
                        current_result *= node.value
                    elif operation == CalculationType.DIVIDE:
                        if node.value != 0:
                            current_result /= node.value
                        else:
                            raise ValueError("Cannot divide by zero!")

            output_node.value = current_result
            self.relationships.append(NodeRelationship(input_nodes=[term[0] for term in input_terms], output_node=output_node, operation=None))

# Sample usage:
funnel = Funnel()
funnel.add_input("Total users", 100)
funnel.add_input("subscribe share", 0.5)
funnel.add_input("number_customers", 10)

relationships = {
    "total subscribers": "total users * subscribe share + number_customers",
    "total clicks": "total subscribers * ctr",
    "total buys": "total clicks * buy rate",
}

funnel.define_relationships(relationships)

for relationship in funnel.relationships:
    relationship.calculate()

print(funnel.get_node("total subscribers").value)  # Outputs the calculated value
# ...
```

#%%
import sympy as sp

# Define symbols
x, y = sp.symbols('x y')

# Create an expression
expr = x**2 + 2*x*y + y**2

# Simplify the expression
simplified_expr = sp.simplify(expr)

# Print the results
print(expr)
print(simplified_expr)
# %%
