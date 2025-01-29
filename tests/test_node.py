import unittest
from decision_analytics import Node, CalculatedNode


class TestNodeCreation(unittest.TestCase):

    def test_create_valid_node(self):
        """Test creating a valid Node."""
        node = Node(
            name="valid_node", format_str=".2%", input_type="input", value=100.0
        )
        self.assertEqual(node.name, "valid_node")
        self.assertEqual(node.format_str, ".2%")
        self.assertEqual(node.input_type, "input")
        self.assertEqual(node.value, 100.0)

    def test_create_valid_calculated_node(self):
        """Test creating a valid CalculatedNode."""
        calc_node = CalculatedNode(
            name="calculated_node",
            definition="valid_node * 2",
            format_str=".2%",
            input_type="calculation",
        )
        self.assertEqual(calc_node.name, "calculated_node")
        self.assertEqual(calc_node.definition, "valid_node * 2")
        self.assertEqual(calc_node.input_type, "calculation")

    def test_create_node_without_value(self):
        """Test raising ValueError for input node without a value."""
        with self.assertRaises(ValueError):
            Node(
                name="node_without_value",
                format_str=".2%",
                input_type="input",  # Missing value
            )

    def test_create_node_with_invalid_input_type(self):
        """Test raising ValueError for invalid input type."""
        with self.assertRaises(ValueError):
            Node(
                name="invalid_input_type_node",
                format_str=".2%",
                input_type="invalid_type",  # Invalid input_type
                value=100.0,
            )

    def test_create_calculated_node_with_non_input_node(self):
        """Test raising ValueError for setting a CalculatedNode as an input node."""
        with self.assertRaises(ValueError):
            CalculatedNode(
                name="invalid_kpi_node",
                definition="another_node * 2",
                format_str=".2%",
                input_type="input",  # Invalid input_type for calculated node
            )

    def test_create_node_with_invalid_value_percentiles(self):
        """Test raising ValueError for invalid value_percentiles length."""
        with self.assertRaises(ValueError):
            Node(
                name="node_with_invalid_percentiles",
                format_str=".2%",
                input_type="input",
                value_percentiles=(0.1, 0.5),  # Should have exactly 3 values
            )

    def test_create_node_with_unsorted_value_percentiles(self):
        """Test raising ValueError for unsorted value_percentiles."""
        with self.assertRaises(ValueError):
            Node(
                name="node_with_unsorted_percentiles",
                format_str=".2%",
                input_type="input",
                value_percentiles=(0.5, 0.1, 0.9),  # Unsorted values
            )


if __name__ == "__main__":
    unittest.main()
