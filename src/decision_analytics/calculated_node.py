from decision_analytics import Node


class CalculatedNode(Node):
    def __init__(self, definition: str, **kwargs):
        self.definition = definition
        assert (
            kwargs.get("input_type") == "calculation"
        ), f"Relation node must be calculation type, got {kwargs.get('input_type')}"
        # pass rest to node init
        super().__init__(**kwargs)
        self.rank = 1

    def __repr__(self):
        node_description = f"{self.name} (Type: {self.input_type}, Definition: {self.definition}, Value:{self._pretty_value()}, Rank: {self.rank})"
        return node_description
