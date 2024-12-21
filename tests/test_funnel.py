import unittest
from decision_tornado.funnel import NodesCollection


class TestNodesCollection(unittest.TestCase):
    def setUp(self):
        self.input_nodes = [
            {
                "name": "total_users",
                "value": 1000000,
                "format_str": "",
                "input_type": "input",
            },
            {
                "name": "subscribe_rate",
                "value": 0.2,
                "format_str": ".2%",
                "input_type": "input",
            },
            {"name": "ctr", "value": 0.2, "format_str": ".2%", "input_type": "input"},
            {
                "name": "sale_success_rate",
                "value": 0.2,
                "format_str": "",
                "input_type": "input",
            },
        ]

        self.relationships = [
            {
                "name": "total_sales",
                "definition": "total_clicks * sale_success_rate",
                "format_str": "",
                "input_type": "calculation",
            },
            {
                "name": "total_subscribers",
                "definition": "total_users * subscribe_rate",
                "format_str": "",
                "input_type": "calculation",
            },
            {
                "name": "total_clicks",
                "definition": "total_subscribers * ctr",
                "format_str": "",
                "input_type": "calculation",
            },
        ]

        self.nodes_collection = NodesCollection()

    def test_add_nodes(self):
        self.nodes_collection.add_nodes(self.input_nodes)
        self.nodes_collection.add_nodes(self.relationships)
        self.assertEqual(len(self.nodes_collection.nodes), 7)

    def test_check_valid_definitions(self):
        self.nodes_collection.add_nodes(self.input_nodes)
        self.nodes_collection.add_nodes(self.relationships)
        try:
            self.nodes_collection.check_valid_definitions()
        except ValueError:
            self.fail("check_valid_definitions() raised ValueError unexpectedly!")

    def test_rank_nodes(self):
        self.nodes_collection.add_nodes(self.input_nodes)
        self.nodes_collection.add_nodes(self.relationships)
        self.nodes_collection.rank_nodes()
        ranks = [node.rank for node in self.nodes_collection.nodes.values()]
        self.assertEqual(ranks, [0, 0, 0, 0, 1, 2, 3])

    def test_get_nonexistent_node(self):
        self.nodes_collection.add_nodes(self.input_nodes)
        self.nodes_collection.add_nodes(self.relationships)
        self.assertIsNone(self.nodes_collection.get_node("nonexistent"))

    def test_update_values(self):
        self.nodes_collection.add_nodes(self.input_nodes)
        self.nodes_collection.add_nodes(self.relationships)
        self.nodes_collection.update_values()
        total_sales = self.nodes_collection.get_node("total_sales")
        self.assertIsNotNone(total_sales, "total_sales node should not be None")
        self.assertAlmostEqual(total_sales.value, 8000.0)


if __name__ == "__main__":
    unittest.main()
