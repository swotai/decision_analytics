import pandas as pd
import plotly.graph_objects as go


def plot_tornado(df: pd.DataFrame, kpi: str) -> go.Figure:
    """
    Plot a tornado chart for the given dataframe and KPI.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the calculated variance swing from the decision funnel.
        Must contain {kpi}_low, {kpi}_mid, {kpi}_high columns, with input variables
        as index.
    kpi : str
        Indicate which KPI is used for the tornado.

    Returns
    -------
    go.Figure
        Plotly graph object instance.
    """
    midpoint = int(df[f"{kpi}_mid"].mode()[0])
    actual_positive = df[f"{kpi}_high"].to_numpy()
    values_positive = actual_positive - midpoint
    actual_negative = df[f"{kpi}_low"].to_numpy()
    values_negative = actual_negative - midpoint
    y = df.index.tolist()

    # Range and range text
    tickvals = [int(min(values_negative)), 0, int(max(values_positive))]
    ticktext = [int(min(actual_negative)), int(midpoint), int(max(actual_positive))]

    layout = go.Layout(
        yaxis=go.layout.YAxis(title="Inputs", categoryorder="array", categoryarray=y),
        xaxis=go.layout.XAxis(
            title="Value",
            # Custom ticks based on midpoint
            tickvals=tickvals,
            # Custom tick labels
            ticktext=ticktext,
        ),
        barmode="overlay",
        bargap=0.1,
    )

    data = [
        # Upper swings
        go.Bar(
            y=y,
            x=values_positive,
            orientation="h",
            name="Lower Swing",
            text=actual_positive.astype("int"),
            hoverinfo="x",
            marker=dict(color="darkturquoise"),
        ),
        # Lower swings
        go.Bar(
            y=y,
            x=values_negative,
            orientation="h",
            name="Upper Swing",
            text=actual_negative.astype("int"),
            hoverinfo="text",
            marker=dict(color="aquamarine"),
        ),
    ]

    return go.Figure(data=data, layout=layout)
