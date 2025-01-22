import re
from decision_tornado import NodesCollection


def generate_funnel_chart_mermaid_code(nodes_collection: NodesCollection):
    """
    Generate mermaid code for a funnel chart
    """
    mermaid_code = """---
config:
  layout: elk
  --look: handDrawn
  theme: forest
---
    
flowchart TD
"""
    for node in nodes_collection.nodes.values():
        mermaid_code += f"    {node.name}([{node.get_chart_str()}])\n"

    for node in nodes_collection.get_calculated_nodes():
        inputs = re.findall(r"\b\w+\b", node.definition)
        for n in inputs:
            n = n.strip()
            mermaid_code += f"    {n} --> {node.name}\n"

    return mermaid_code


# Tornado Chart
