import pytest
import pandas as pd
from decision_analytics.plotting_utils.tornado import plot_tornado
import plotly.graph_objects as go


def test_plot_tornado():
    data = {
        "input1": {
            "kpi1_low": 90,
            "kpi1_mid": 100,
            "kpi1_high": 110,
            "kpi1_swing_squared": 20,
        },
        "input2": {
            "kpi1_low": 80,
            "kpi1_mid": 100,
            "kpi1_high": 120,
            "kpi1_swing_squared": 40,
        },
    }
    df = pd.DataFrame(data).T
    figure = plot_tornado(df, "kpi1")
    assert isinstance(figure, go.Figure)
