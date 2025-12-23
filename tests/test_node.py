import pytest

from decision_analytics import Node


def test_node_initialization():
    node = Node(
        name="node1",
        format_str=".2f",
        node_type="input",
        value=100.0,
    )
    assert node.name == "node1"
    assert node.format_str == ".2f"
    assert node.node_type == "input"
    assert node.value == 100.0


def test_node_invalid_node_type():
    with pytest.raises(ValueError):
        Node(name="node2", format_str=".2f", node_type="undefined")


def test_node_without_value_for_input():
    with pytest.raises(ValueError):
        Node(name="node3", format_str=".2f", node_type="input")


def test_pretty_value():
    node = Node(name="node4", format_str=".2f", node_type="input", value=1234.56)
    assert node._pretty_value() == "1.23 K"
