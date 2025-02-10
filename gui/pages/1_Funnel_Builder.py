import streamlit as st
import pandas as pd
import ast
from decision_analytics import Node, CalculatedNode, Funnel


def update_nodes_from_dataframe(edited_df, node_type="input"):
    """Update nodes collection from edited dataframe"""
    try:
        for _, row in edited_df.iterrows():
            node_data = {
                "name": row["Name"],
                "long_name": row["Long Name"],
                "description": row["Description"],
                "format_str": row["Format"],
                "is_kpi": row["Is KPI"],
                "input_type": row["Input Type"],
            }
            if node_type == "input":
                # Handle value percentiles
                try:
                    if pd.notna(row["Value Percentiles"]):
                        percentiles = ast.literal_eval(row["Value Percentiles"])
                        if isinstance(percentiles, (list, tuple)):
                            node_data["value_percentiles"] = tuple(percentiles)
                except:
                    node_data["value_percentiles"] = None

                node_data["value"] = row["Value"] if pd.notna(row["Value"]) else None
            else:
                node_data["definition"] = row["Definition"]
                node_data["value"] = None

            # Update or add node to collection
            st.session_state.nodes_collection.add_nodes([node_data])

        # Refresh calculations
        st.session_state.nodes_collection.refresh_nodes()
        st.session_state.funnel = Funnel(st.session_state.nodes_collection)
        st.session_state.funnel.simulate()
    except Exception as e:
        st.error(f"Error updating nodes: {str(e)}")


st.title("Funnel Builder")

# Split the page into two columns
left_col, right_col = st.columns([0.6, 0.4])

with left_col:
    # Input Nodes Table
    st.subheader("Input Nodes")
    input_nodes = st.session_state.nodes_collection.get_input_nodes()
    if input_nodes:
        input_df = pd.DataFrame(
            [
                {
                    "Name": node.name,
                    "Long Name": node.long_name,
                    "Description": node.description,
                    "Value": node.value,
                    "Value Percentiles": str(node.value_percentiles),
                    "Format": node.format_str,
                    "Is KPI": node.is_kpi,
                    "Input Type": node.input_type,
                }
                for node in input_nodes
            ]
        )
        edited_input_df = st.data_editor(
            input_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Name": st.column_config.TextColumn("Name", required=True),
                "Long Name": st.column_config.TextColumn("Long Name", required=True),
                "Description": st.column_config.TextColumn("Description"),
                "Value": st.column_config.NumberColumn("Value"),
                "Value Percentiles": st.column_config.TextColumn("Value Percentiles"),
                "Format": st.column_config.TextColumn("Format"),
                "Is KPI": st.column_config.CheckboxColumn("Is KPI"),
                "Input Type": st.column_config.TextColumn("Input Type"),
            },
        )
    else:
        st.info("No input nodes available")

    # Calculated Nodes Table
    st.subheader("Calculated Nodes")
    calc_nodes = st.session_state.nodes_collection.get_calculated_nodes()
    if calc_nodes:
        calc_df = pd.DataFrame(
            [
                {
                    "Name": node.name,
                    "Long Name": node.long_name,
                    "Description": node.description,
                    "Definition": node.definition,
                    "Value": node.value,
                    "Format": node.format_str,
                    "Is KPI": node.is_kpi,
                    "Input Type": node.input_type,
                }
                for node in calc_nodes
            ]
        )
        edited_calc_df = st.data_editor(
            calc_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Name": st.column_config.TextColumn("Name", required=True),
                "Long Name": st.column_config.TextColumn("Long Name", required=True),
                "Description": st.column_config.TextColumn("Description"),
                "Definition": st.column_config.TextColumn("Definition", required=True),
                "Value": st.column_config.NumberColumn("Value", disabled=True),
                "Format": st.column_config.TextColumn("Format"),
                "Is KPI": st.column_config.CheckboxColumn("Is KPI"),
                "Input Type": st.column_config.TextColumn("Input Type"),
            },
        )
    else:
        st.info("No calculated nodes available")

    # Update nodes collection if input table was edited
    if (
        input_nodes
        and edited_input_df is not None
        and not edited_input_df.equals(input_df)
    ):
        update_nodes_from_dataframe(edited_input_df, "input")

    # Update nodes collection if calculated table was edited
    if calc_nodes and edited_calc_df is not None and not edited_calc_df.equals(calc_df):
        update_nodes_from_dataframe(edited_calc_df, "calculation")

with right_col:
    st.subheader("Flowchart")
    # Generate mermaid chart
    mermaid_code = "graph TD\n"

    # Add all nodes first
    for node in st.session_state.nodes_collection:
        node_style = "default"
        if isinstance(node, CalculatedNode):
            node_style = "rounded"
        if node.is_kpi:
            node_style = "stadium"
        mermaid_code += f"    {node.name}[{node.name}]:::{node_style}\n"

    # Add relationships for calculated nodes
    for node in st.session_state.nodes_collection:
        if isinstance(node, CalculatedNode):
            # Extract dependencies from definition using regex to handle operators
            import re

            deps = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", node.definition)
            for dep in deps:
                if dep in st.session_state.nodes_collection.nodes:
                    mermaid_code += f"    {dep} --> {node.name}\n"

    # Add style definitions
    mermaid_code += """
    classDef default fill:#ddd,stroke:#000,stroke-width:1px;
    classDef rounded fill:#bbf,stroke:#000,stroke-width:1px,rx:10px,ry:10px;
    classDef stadium fill:#bfb,stroke:#000,stroke-width:1px,rx:20px,ry:20px;
    """

    # Display mermaid chart
    st.markdown(f"```mermaid\n{mermaid_code}\n```")
