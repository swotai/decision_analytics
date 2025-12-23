import pandas as pd
import pytest

from decision_analytics import Funnel, NodesCollection


def setup_nodes():
    collection = NodesCollection()
    input_node = {
        "name": "input1",
        "format_str": "",
        "node_type": "input",
        "value": 10,
        "value_low": 8,
        "value_mid": 10,
        "value_high": 12,
    }
    input_node2 = {
        "name": "input2",
        "format_str": "",
        "node_type": "input",
        "value": 3,
        "value_low": 2,
        "value_mid": 3,
        "value_high": 10,
    }
    input_node_3 = {
        "name": "input3",
        "format_str": "",
        "node_type": "input",
        "value": 3,
        "value_low": 0.25,
        "value_mid": 0.9,
        "value_high": 2.45,
    }
    calculated_node = {
        "name": "output1",
        "definition": "input1 * input2",
        "format_str": "",
        "node_type": "calculation",
        "is_kpi": True,
    }
    calculated_node2 = {
        "name": "output2",
        "definition": "input2 * input3",
        "format_str": "",
        "node_type": "calculation",
        "is_kpi": True,
    }
    collection.add_nodes(
        [
            input_node,
            input_node2,
            input_node_3,
            calculated_node,
            calculated_node2,
        ]
    )
    return collection


def test_simulate_input_variance():
    nodes_collection = setup_nodes()
    funnel = Funnel(nodes_collection=nodes_collection)
    input_var = funnel.simulate_input_variance()
    input_var.to_csv("input_var.csv")
    assert isinstance(input_var, pd.DataFrame)
    assert "input1" in input_var.columns


def test_calculate_inputs_swing():
    nodes_collection = setup_nodes()
    funnel = Funnel(nodes_collection=nodes_collection)
    funnel.simulate_input_variance()
    input_swing = funnel.calculate_inputs_swing()
    input_swing.to_csv("input_swing.csv")
    assert isinstance(input_swing, pd.DataFrame)
    assert "output1_swing" in input_swing.columns
