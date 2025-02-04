# Decision Analytics

A Python library for decision analysis that enables the creation and analysis of decision funnels with uncertainty modeling. This package helps you understand how variations in input parameters affect your key performance indicators (KPIs) through visualization tools and statistical analysis.

## Features

- Create decision funnels with interconnected nodes and relationships
- Model uncertainty using value ranges (10, 50, 90th percentile) for input parameters
- Generate tornado diagrams to visualize sensitivity analysis
- Create cumulative distribution function (CDF) and probability density function (PDF) plots
- Calculate combined uncertainty effects across multiple input variables
- Metalogistic distribution fitting for probabilistic analysis

## Installation

You can install the package using pip:

```bash
pip install decision_analytics
```

Requirements:

- Python ≥ 3.11
- pandas
- plotly
- nbformat

## Usage Example

Here's a simple example of how to create a decision funnel analyzing a user conversion process:

```python
from decision_analytics import NodesCollection, Funnel
from decision_analytics.utils import setup_logging
import logging

# Set up logging (optional)
setup_logging(level=logging.INFO)

# Define input nodes with their values and uncertainty ranges
input_nodes = [
    {
        "name": "total_users",
        "value": 10000,
        "format_str": "",
        "input_type": "input",
        "value_percentiles": (0.1 * 10000, 0.5 * 10000, 0.9 * 10000),
    },
    {
        "name": "subscribe_rate",
        "value": 0.5,
        "format_str": ".2%",
        "input_type": "input",
        "value_percentiles": (0.45, 0.5, 0.6),
    },
    {
        "name": "ctr",
        "long_name": "Click-Through Rate",
        "value": 0.1,
        "format_str": ".2%",
        "input_type": "input",
        "value_percentiles": (0.08, 0.1, 0.11),
    },
    {
        "name": "sale_success_rate",
        "value": 0.3,
        "format_str": ".2%",
        "input_type": "input",
        "value_percentiles": (0.1, 0.3, 0.5),
    },
]

# Define relationships between nodes
relationships = [
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
    {
        "name": "total_sales",
        "definition": "total_clicks * sale_success_rate",
        "format_str": "",
        "input_type": "calculation",
        "is_kpi": True,
    },
]

# Create and populate the nodes collection
nodes = NodesCollection()
nodes.add_nodes(input_nodes)
nodes.add_nodes(relationships)
nodes.refresh_nodes()

# Create a funnel for analysis
funnel = Funnel(nodes_collection=nodes)

# Run simulation and get results
funnel.simulate_variances()
results = funnel.update_calculations()

# Generate visualizations
kpi = "total_sales"

# Create a tornado chart to visualize input sensitivities
funnel.get_tornado_chart(kpi)

# Generate probability distribution charts
funnel.get_cumulative_chart(kpi)  # Cumulative distribution
funnel.get_pdf_chart(kpi)         # Probability density function
funnel.get_cdf_chart(kpi)         # Cumulative distribution function

# Get metalogistic distribution for advanced analysis
metalog = funnel.get_metalog(kpi)
print(f"80th percentile: {metalog.quantile([0.8])[0]}")
print(f"99th percentile: {metalog.quantile([0.99])[0]}")
metalog.print_summary()
```

This basic example demonstrates how to:

1. Create input nodes with uncertainty ranges (low/mid/high values)
2. Define calculated nodes and relationships
3. Run simulations to understand the impact of input variations
4. Generate various visualization types for analysis
5. Use the metalogistic distribution for probabilistic insights

The package provides visualization tools to help understand:

- Which input variables have the largest impact on your KPIs (tornado charts)
- The probability distribution of your KPIs (PDF/CDF plots)
- The cumulative effect of all uncertainties combined
