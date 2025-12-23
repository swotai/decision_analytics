import pytest
from decision_analytics import CalculatedNode


def test_calculated_node_initialization():
    node = CalculatedNode(
        definition="x + y", name="node1", format_str=".2f", node_type="calculation"
    )
    assert node.definition == "x + y"
    assert node.rank == 1


def test_calculated_node_wrong_type():
    with pytest.raises(AssertionError):
        CalculatedNode(
            definition="z * 2", name="node2", format_str=".2f", node_type="input"
        )
