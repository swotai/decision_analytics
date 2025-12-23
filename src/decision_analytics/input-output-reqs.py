# %%
# Requirements:
# Code should be able to read from json with a list of predefined inputs
# Code should be able to read from json for a list of relationships specifying how the inputs are used
# the input and relationship json can be converted from excel/csv

# %%
# Sample input nodes:

input = [
    {"name": "total_users", "value": 1000000, "format": "", "node_type": "input"},
    {"name": "subscribe_rate", "value": 0.2, "format": ".2%", "node_type": "input"},
    {"name": "ctr", "value": 0.2, "format": ".2%", "node_type": "input"},
    {"name": "sale_success_rate", "value": 0.2, "format": "", "node_type": "input"},
]


# %%
# Sample relationship

relationships = [
    {
        "name": "total_subscribers",
        "definition": "total_users * subscribe_rate",
        "format": "",
        "node_type": "calculation",
    },
    {
        "name": "total_clicks",
        "definition": "total_subscribers * ctr",
        "format": "",
        "node_type": "calculation",
    },
    {
        "name": "total_sales",
        "definition": "total_clicks * sale_success_rate",
        "format": "",
        "node_type": "calculation",
    },
    {
        "name": "conversion_rate",
        "definition": "subscribe_rate * ctr * buy_rate",
        "format": "",
        "node_type": "calculation",
    },
]
