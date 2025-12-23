from decision_analytics import Node


class CalculatedNode(Node):
    def __init__(self, definition: str, **kwargs):
        super().__init__(**kwargs)
        self.definition = definition
        assert (
            kwargs.get("node_type") == "calculation"
        ), f"Relation node must be calculation type, got {kwargs.get('node_type')} for node {self.name}"
        # pass rest to node init
        self.rank = 1

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.node_type}, Definition: {self.definition}, Value:{self._pretty_value()}, Rank: {self.rank})"
        return node_description
