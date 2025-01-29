import pytest
from decision_analytics.flow_charting import generate_funnel_chart_mermaid_code
from decision_analytics.nodes_collection import NodesCollection


def test_generate_funnel_chart_mermaid_code():
    collection = NodesCollection()
    node = {"name": "node1", "format_str": "", "input_type": "input", "value": 10}
    collection.add_nodes([node])
    collection.add_nodes(
        [
            {
                "name": "calculated_node",
                "definition": "node1 * 2",
                "format_str": "",
                "input_type": "calculation",
            }
        ]
    )
    mermaid_code = generate_funnel_chart_mermaid_code(collection)
    assert "node1" in mermaid_code
    assert "calculated_node" in mermaid_code
