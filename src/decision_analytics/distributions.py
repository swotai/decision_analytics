import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from decision_analytics.metalogistic import MetaLogistic


def generate_cumulative_distribution_chart(
    data: pd.DataFrame, kpi: str
) -> matplotlib.pyplot:
    sorted_data = data.sort_values(by=kpi, ascending=True).reset_index(drop=True)
    weights = sorted_data["weights"].to_numpy()
    cumulative_pr = np.cumsum(weights)
    kpi_values = sorted_data[kpi].to_numpy()

    # Cumulative Distribution
    plt.figure(figsize=(10, 6))
    plt.plot(kpi_values, cumulative_pr, marker="o")  # Create a line plot with markers
    plt.xlabel("KPI (Total Sales)")
    plt.ylabel("Cumulative Weights")
    plt.title("KPI vs Cumulative Weights")
    # Optional: Add a grid for better readability
    plt.grid()
    # Display the plot
    plt.show()
    return plt


def generate_combined_uncertainty_cdf_with_metalog(
    data: pd.DataFrame, kpi: str
) -> matplotlib.pyplot:
    result = data.loc[
        "Combined_Uncertainty", [f"{kpi}_low", f"{kpi}_mid", f"{kpi}_high"]
    ]
    result.tolist()
    my_metalog = MetaLogistic(cdf_xs=result.tolist(), cdf_ps=[0.1, 0.5, 0.9])

    return plt


if False:
    a = a.sort_values(by="total_sales", ascending=True).reset_index(drop=True)
    p = a["weights"].to_numpy()
    c = np.cumsum(p)
    kpi = a["total_sales"].to_numpy()

    # Metalog fitted smooth distribution
    # using the spread of the kpi in calculation
    kpi = "total_sales"
    result = b.loc["Combined Uncertainty", [f"{kpi}_low", f"{kpi}_mid", f"{kpi}_high"]]
    result.tolist()

    # Don't try to fit the whole kpi + cumu weights! go from the spread.
    # my_metalog = MetaLogistic(cdf_xs=kpi, cdf_ps=c)
    my_metalog = MetaLogistic(cdf_xs=result.tolist(), cdf_ps=[0.1, 0.5, 0.9])

    # These methods can take scalars or arrays/lists/vectors
    my_metalog.cdf(10)
    my_metalog.pdf([10, 20, 21])
    my_metalog.quantile([0.8, 0.99])

    # These methods conveniently display useful information
    my_metalog.print_summary()
    my_metalog.display_plot()
