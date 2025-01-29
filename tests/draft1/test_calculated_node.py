def test_calculated_node():
    input_nodes = [InputNode(name="a", value=2), InputNode(name="b", value=3)]
    node = CalculatedNode(name="sum", definition=lambda a, b: a + b, format_str="%d")
    nodes = NodesCollection(input_nodes)
    nodes.add_nodes([node])
    nodes.refresh_nodes()

    assert nodes.get_node("sum").value == 5
