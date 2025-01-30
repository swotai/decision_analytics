import matplotlib.pyplot as plt
import numpy as np

from decision_analytics.metalogistic import MetaLogistic

a = a.sort_values(by="total_sales", ascending=True).reset_index(drop=True)
p = a["weights"].to_numpy()
c = np.cumsum(p)
kpi = a["total_sales"].to_numpy()


# Cumulative Distribution
plt.figure(figsize=(10, 6))
plt.plot(kpi, c, marker="o")  # Create a line plot with markers
plt.xlabel("KPI (Total Sales)")
plt.ylabel("Cumulative Weights")
plt.title("KPI vs Cumulative Weights")
plt.grid()  # Optional: Add a grid for better readability
plt.show()  # Display the plot

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
