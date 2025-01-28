kpi = "total_sales"

import plotly.graph_objects as go

midpoint = int(b[f"{kpi}_mid"].mode()[0])
actual_positive = b[f"{kpi}_high"].to_numpy()
values_positive = actual_positive - midpoint
actual_negative = b[f"{kpi}_low"].to_numpy()
values_negative = actual_negative - midpoint
y = b.index.tolist()

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
        # name="Men",
        text=actual_positive.astype("int"),
        hoverinfo="x",
        marker=dict(color="powderblue"),
    ),
    # Lower swings
    go.Bar(
        y=y,
        x=values_negative,
        orientation="h",
        name="Women",
        text=actual_negative.astype("int"),
        hoverinfo="text",
        marker=dict(color="seagreen"),
    ),
]

# py.iplot(dict(data=data, layout=layout), filename="EXAMPLES/bar_pyramid")
go.Figure(data=data, layout=layout)
