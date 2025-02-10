import numpy as np
import pandas as pd
import plotly.graph_objects as go

from decision_analytics.metalogistic import MetaLogistic


def generate_cumulative_distribution_chart(data: pd.DataFrame, kpi: str) -> go.Figure:
    sorted_data = data.sort_values(by=kpi, ascending=True).reset_index(drop=True)
    weights = sorted_data["weights"].to_numpy()
    cumulative_pr = np.cumsum(weights)
    kpi_values = sorted_data[kpi].to_numpy()

    # Cumulative Distribution
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=kpi_values, y=cumulative_pr, mode="lines+markers"))
    fig.update_layout(
        title=f"KPI ({kpi}) vs Cumulative Weights",
        xaxis_title="KPI (Total Sales)",
        yaxis_title="Cumulative Weights",
        height=600,
        width=800,
    )
    return fig


def display_cdf_plot(cdf_data: dict, kpi: str) -> go.Figure:
    """
    Plots the Cumulative Distribution Function (CDF) of the metalog.
    """

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cdf_data["X-values"],
            y=cdf_data["Probabilities"],
            mode="lines",
            name="CDF",
        )
    )
    fig.update_layout(
        title=f"Cumulative Distribution Function (CDF) - {kpi}",
        xaxis_title=f"Possible value of {kpi}",
        yaxis_title="Probability",
    )
    # fig.show()
    return fig


def display_pdf_plot(
    pdf_data: dict,
    kpi: str,
    hide_extreme_densities=50,
) -> go.Figure:
    """
    Plots the Probability Density Function (PDF) of the metalog.

    The parameter `hide_extreme_densities` is used on the PDF plot, to set its y-axis maximum to `hide_extreme_densities` times
    the median density. This is because, when given extreme input data, the resulting metalog might have very short but extremely tall spikes in the PDF
    (where the maximum density might be in the hundreds), which would make the PDF plot unreadable if the entire spike was included.

    """

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pdf_data["X-values"], y=pdf_data["Densities"], mode="lines", name="PDF"
        )
    )

    if hide_extreme_densities:
        density50 = np.percentile(pdf_data["Densities"], 50)
        pdf_max_display = min(
            density50 * hide_extreme_densities, 1.05 * max(pdf_data["Densities"])
        )
        fig.update_layout(yaxis_range=[0, pdf_max_display])

    fig.update_layout(
        title=f"Probability Density Function (PDF) - {kpi}",
        xaxis_title=f"Possible value of {kpi}",
        yaxis_title="Density",
    )
    # fig.show()
    return fig
