def test_nodes_collection():
    collection = NodesCollection()
    input1 = InputNode(name="a", value=2)
    input2 = InputNode(name="b", value=3)
    collection.add_nodes([input1, input2])

    assert len(collection.nodes) == 2

    # Add a calculated node
    sum_node = CalculatedNode(
        name="sum", definition=lambda x, y: x + y, format_str="%d"
    )
    collection.add_nodes([sum_node])
    collection.refresh_nodes()

    values = collection.get_values_from_dict({"a": 2, "b": 3})
    assert sum_node.value == 5
