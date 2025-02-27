import pandas as pd
import pytest

from decision_analytics import Funnel, NodesCollection


def setup_nodes():
    collection = NodesCollection()
    input_node = {
        "name": "input1",
        "format_str": "",
        "input_type": "input",
        "value": 10,
        "value_percentiles": (8, 10, 12),
    }
    calculated_node = {
        "name": "output1",
        "definition": "input1 * 2",
        "format_str": "",
        "input_type": "calculation",
        "is_kpi": True,
    }
    collection.add_nodes([input_node, calculated_node])
    return collection


def test_simulate_variances():
    nodes_collection = setup_nodes()
    funnel = Funnel(nodes_collection=nodes_collection)
    result = funnel.simulate_variances()
    assert isinstance(result, pd.DataFrame)
    assert "input1" in result.columns


def test_update_calculations():
    nodes_collection = setup_nodes()
    funnel = Funnel(nodes_collection=nodes_collection)
    funnel.simulate_variances()
    calculations = funnel.update_calculations()
    assert isinstance(calculations, pd.DataFrame)
    assert "output1_swing" in calculations.columns
