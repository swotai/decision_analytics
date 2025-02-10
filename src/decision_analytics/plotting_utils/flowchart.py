import re
from decision_analytics import NodesCollection


def generate_funnel_chart_mermaid_code(nodes_collection: NodesCollection) -> str:
    """
    Generate mermaid code for a funnel chart
    """
    mermaid_code = """---
config:
  layout: elk
  theme: forest
---
flowchart TD
"""
    for node in nodes_collection.nodes.values():
        node_style = "default"
        if node.input_type == "calculation":
            node_style = "rounded"
        if node.is_kpi:
            node_style = "stadium"
        mermaid_code += f"    {node.name}[{node.get_chart_str()}]:::{node_style}\n"

    for node in nodes_collection.get_calculated_nodes():
        inputs = re.findall(r"\b\w+\b", node.definition)
        for n in inputs:
            n = n.strip()
            mermaid_code += f"    {n} --> {node.name}\n"

    mermaid_code += """
    classDef default fill:#ddd,stroke:#000,stroke-width:1px;
    classDef rounded fill:#bbf,stroke:#000,stroke-width:1px,rx:10px,ry:10px;
    classDef stadium fill:#bfb,stroke:#000,stroke-width:1px,rx:20px,ry:20px;
    """
    return mermaid_code


# Tornado Chart
