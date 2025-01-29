def test_flow_chart():
    # Use sample nodes (similar to funnel.py flow_charting.py)
    mermaid_code = generate_funnel_chart_mermaid_code(nodes_collection=test)
    assert "graph TD" in mermaid_code
