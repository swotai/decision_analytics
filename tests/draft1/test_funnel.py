def test_funnel_simulation():
    # Set up input nodes with percentile values
    a = InputNode("a", value=10, value_percentiles=(5, 10, 15))
    b = InputNode("b", value=20, value_percentiles=(40, 50, 60))

    # Create relationships and nodes (similar to sandbox_funnel.py)
    relationships = [
        {
            "name": "sum",
            "definition": lambda a, b: a + b,
            "format_str": "",
            "input_type": "calculation",
        },
    ]

    test = NodesCollection()
    test.add_nodes([a])
    test.add_nodes(relationships)
    test.refresh_nodes()

    results = test.simulate_variances()
    assert "total_sales_swing_squared" in results.columns
