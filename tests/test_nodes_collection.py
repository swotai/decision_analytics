import pytest
from decision_analytics.nodes_collection import NodesCollection
from decision_analytics.node import Node


def test_add_single_node():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "input_type": "input", "value": 10}
    collection.add_nodes([node])
    assert len(collection.nodes) == 1
    assert collection.get_node("node1").value == 10


def test_get_nonexistent_node():
    collection = NodesCollection()
    with pytest.raises(ValueError):
        collection.get_node("nonexistent_node")


def test_remove_node():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "input_type": "input", "value": 10}
    collection.add_nodes([node])
    collection.remove_node("node1")
    assert len(collection.nodes) == 0
