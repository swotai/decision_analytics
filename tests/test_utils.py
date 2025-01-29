import pytest
from decision_analytics.utils import format_float


def test_format_float_basic():
    assert format_float(1234.56, ".2f") == "1.23 K"


def test_format_float_no_millify():
    assert format_float(1234567890, ".0f", False) == "1234567890"
