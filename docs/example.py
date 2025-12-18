# %%
from decision_analytics import NodesCollection, Funnel
from decision_analytics.utils import setup_logging
import logging

setup_logging(level=logging.INFO)

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

test = NodesCollection()
test.add_nodes(input_nodes)
test.add_nodes(relationships)
test.refresh_nodes()
total_sales = test.get_node("total_sales")
print(total_sales.value)


# %%
testf = Funnel(nodes_collection=test)
a = testf.simulate_input_variance()
a

# %%
b = testf.calculate_inputs_swing()
b = b.sort_values(by="total_sales_swing_squared", ascending=True, na_position="first")
# %%
kpi = "total_sales"
# %%
testf.get_tornado_chart(kpi)
# %%
testf.get_cumulative_chart(kpi)
# %%
my_metalog = testf.get_metalog(kpi)
print(my_metalog.cdf(10))
print(my_metalog.pdf([10, 20, 21]))
print(my_metalog.quantile([0.8, 0.99]))
my_metalog.print_summary()
# my_metalog.display_plot()

# %%
testf.get_cdf_chart(kpi)

# %%
testf.get_pdf_chart(kpi)
# %%
