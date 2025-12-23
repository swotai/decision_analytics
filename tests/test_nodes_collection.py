import pytest

from decision_analytics import NodesCollection


def test_add_single_node():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    collection.add_nodes([node])
    assert len(collection.nodes) == 1
    assert collection.get_node("node1").value == 10


def test_get_nonexistent_node():
    collection = NodesCollection()
    with pytest.raises(ValueError):
        collection.get_node("nonexistent_node")


def test_remove_node():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    collection.add_nodes([node])
    collection.remove_node("node1")
    assert len(collection.nodes) == 0


def test_set_node_values_from_dict_success():
    collection = NodesCollection()
    node = {
        "name": "node1",
        "format_str": "",
        "node_type": "input",
        "value": 10,
        # "value_percentiles": (5, 10, 15),
        "value_low": 5,
        "value_mid": 10,
        "value_high": 15,
    }
    collection.add_nodes([node])
    collection.set_node_values_from_dict({"node1": 1})
    assert collection.get_node("node1").value == 10
    collection.set_node_values_from_dict({"node1": 100}, lookup=False)
    assert collection.get_node("node1").value == 100


def test_set_node_values_from_dict_node_not_exist():
    collection = NodesCollection()
    with pytest.raises(ValueError, match="Node 'nonexistent_node' does not exist."):
        collection.set_node_values_from_dict({"nonexistent_node": 1})


def test_set_node_values_from_dict_calculated_node():
    collection = NodesCollection()
    node = {
        "name": "node1",
        "format_str": "",
        "node_type": "calculation",
        "definition": "1+1",
    }
    collection.add_nodes([node])
    with pytest.raises(
        ValueError, match="Cannot set value for calculated node 'node1'."
    ):
        collection.set_node_values_from_dict({"node1": 1})


def test_set_node_values_from_dict_invalid_number():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    collection.add_nodes([node])
    with pytest.raises(
        ValueError, match="Value 'abc' is not a valid number for node 'node1'."
    ):
        collection.set_node_values_from_dict({"node1": "abc"})


def test_set_node_values_from_dict_invalid_lookup_value():
    collection = NodesCollection()
    node = {
        "name": "node1",
        "format_str": "",
        "node_type": "input",
        "value": 10,
        "value_low": 5,
        "value_mid": 10,
        "value_high": 15,
    }
    collection.add_nodes([node])
    with pytest.raises(
        ValueError,
        match="When using lookup, value must be 0, 1, or 2 for 10th, 50th, or 90th percentile. Got 5",
    ):
        collection.set_node_values_from_dict({"node1": 5})


def test_set_node_values_from_dict_key_error():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    collection.add_nodes([node])
    with pytest.raises(ValueError, match="Node 'nodeX' does not exist."):
        collection.set_node_values_from_dict({"nodeX": 20})


def test_set_node_values_from_dict_no_percentiles():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    collection.add_nodes([node])
    collection.set_node_values_from_dict({"node1": 20}, lookup=False)
    assert collection.get_node("node1").value == 20


def test_to_json():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
    }
    collection.add_nodes([node1, node2])
    json_str = collection.to_json_str()
    assert isinstance(json_str, str)
    assert "node1" in json_str
    assert "node2" in json_str
    assert "definition" in json_str


def test_from_json_success():
    collection = NodesCollection()
    json_data = """
    [
        {
            "name": "nodeA",
            "format_str": "",
            "node_type": "input",
            "value": 5,
            "is_kpi": false,
            "readable_large_number": false
        },
        {
            "name": "nodeB",
            "format_str": "",
            "node_type": "calculation",
            "definition": "nodeA * 10",
            "is_kpi": true,
            "readable_large_number": false
        }
    ]
    """
    collection.from_json_str(json_data)
    assert len(collection.nodes) == 2
    assert collection.get_node("nodeA").value == 5
    assert collection.nodes["nodeB"].definition == "nodeA * 10"


def test_from_json_invalid_json_string():
    collection = NodesCollection()
    with pytest.raises(ValueError, match="Invalid JSON string"):
        collection.from_json_str("invalid json")


def test_from_json_not_list():
    collection = NodesCollection()
    with pytest.raises(
        ValueError, match="JSON must contain a list of node definitions"
    ):
        collection.from_json_str('{"name": "node1"}')


def test_get_unused_nodes():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
    }
    node3 = {"name": "node3", "format_str": "", "node_type": "input", "value": 5}
    collection.add_nodes([node1, node2, node3])
    unused_nodes = collection.get_unused_nodes()
    assert len(unused_nodes) == 1
    assert unused_nodes[0].name == "node3"


def test_check_valid_definitions_success():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 + 2",
    }
    collection.add_nodes([node1, node2])
    # No exception should be raised


def test_check_valid_definitions_invalid_variable():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 + nodeX",
    }
    with pytest.raises(
        ValueError, match="Variable 'nodeX' in node 'node2' is not a valid input node."
    ):
        collection.add_nodes([node1, node2])


def test_check_valid_definitions_invalid_character():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 @ 2",
    }
    with pytest.raises(
        ValueError, match="Invalid character '@' in definition of node 'node2'."
    ):
        collection.add_nodes([node1, node2])


def test_rank_nodes_success():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
    }
    node3 = {
        "name": "node3",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node2 + 5",
    }
    collection.add_nodes([node1, node2, node3])
    assert collection.get_node("node1").rank == 0
    assert collection.get_node("node2").rank == 1
    assert collection.get_node("node3").rank == 2


def test_rank_nodes_unresolvable_dependency():
    collection = NodesCollection()
    node1 = {
        "name": "node1",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node2 + 1",
    }
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
    }
    with pytest.raises(ValueError, match="Unresolvable dependencies detected"):
        collection.add_nodes([node1, node2])


def test_refresh_nodes_no_kpi_warning(caplog):
    import logging

    caplog.set_level(logging.WARNING)

    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
        "is_kpi": False,
    }
    collection.add_nodes([node1, node2])
    collection.refresh_nodes()
    assert "No calculated node designated in the nodes collection." in caplog.text


def test_reset_input_nodes_with_percentiles():
    collection = NodesCollection()
    node = {
        "name": "node1",
        "format_str": "",
        "node_type": "input",
        "value": 10,
        "value_low": 5,
        "value_mid": 10,
        "value_high": 15,
    }
    collection.add_nodes([node])
    collection.get_node("node1").value = 99  # Change value to ensure it resets
    collection.reset_input_nodes()
    assert (
        collection.get_node("node1").value == 10
    )  # Should reset to median (index 1 of percentiles)


def test_reset_input_nodes_without_percentiles():
    collection = NodesCollection()
    node = {
        "name": "node1",
        "format_str": "",
        "node_type": "input",
        "value": 10,
        "value_low": None,
        "value_mid": None,
        "value_high": None,
    }
    collection.add_nodes([node])
    collection.get_node("node1").value = (
        99  # Change value to ensure it remains unchanged
    )
    collection.reset_input_nodes()
    assert (
        collection.get_node("node1").value == 99
    )  # Should not change if no percentiles


def test_repr():
    collection = NodesCollection()
    node1 = {"name": "node1", "format_str": "", "node_type": "input", "value": 10}
    node2 = {
        "name": "node2",
        "format_str": "",
        "node_type": "calculation",
        "definition": "node1 * 2",
    }
    collection.add_nodes([node1, node2])
    assert (
        "NodesCollection with 2 nodes: 1 input nodes and 1 calculated nodes."
        == collection.__repr__()
    )
