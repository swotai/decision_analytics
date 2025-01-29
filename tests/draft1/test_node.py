import pytest

from decision_analytics import Node


@pytest.fixture
def node():
    return Node(name="TestNode", value=10)


def test_node_initialization(node):
    assert node.value == 10
    assert isinstance(node.value, int)
    with pytest.raises(ValueError):
        Node(name="InvalidNode", value=None)  # value should be a number


def test_value_update(node):
    node.update(5.0)
    assert node.value == 5.0


def test_safe_evaluation():
    safe_eval = lambda x: x + 2
    node.value = 3.0
    result = safe_eval(node)
    assert isinstance(result, float)
    assert result == 5.0


def test_input_node():
    node = InputNode(name="test", value=10, format_str="%d")
    assert node.name == "test"
    assert node.value == 10
    assert node.format_str == "%d"


def test_kpin_node():
    node = KpinNode(name="kpi-test", label="Test KPI", low=1, mid=2, high=3)
    assert node.name == "kpi-test"
    assert node.label == "Test KPI"
    assert node.low == 1
    assert node.mid == 2
