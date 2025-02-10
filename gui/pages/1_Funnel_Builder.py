import ast

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from decision_analytics import Funnel
from decision_analytics.plotting_utils.flowchart import (
    generate_funnel_chart_mermaid_code,
)


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
    mermaid_code = generate_funnel_chart_mermaid_code(st.session_state.nodes_collection)
    components.html(
        f"""<pre class="mermaid">{mermaid_code}</pre>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true }});
    </script>
        """,
        height=600,
        scrolling=True,
    )


# Get KPI nodes
kpi_nodes = st.session_state.nodes_collection.get_kpi_nodes()
if kpi_nodes:
    # Create a row with two columns for KPI selection and refresh button
    kpi_col, refresh_col = st.columns([0.7, 0.3], vertical_alignment="bottom")

    with kpi_col:
        # Create a selectbox for KPI selection
        selected_kpi = st.selectbox(
            "Select KPI to display",
            options=[node.name for node in kpi_nodes],
            format_func=lambda x: st.session_state.nodes_collection.get_node(
                x
            ).long_name,
        )

    with refresh_col:
        # Add refresh button
        if st.button("Refresh Calculation"):
            # Update the funnel calculations
            st.session_state.funnel.simulate()

    # Split the page into two columns
    left_col, right_col = st.columns([0.5, 0.5])
    with left_col:
        # Get and display tornado chart
        try:
            tornado_fig = st.session_state.funnel.get_tornado_chart(selected_kpi)
            st.plotly_chart(tornado_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating tornado chart: {str(e)}")

    with right_col:
        # Display cumulative chart
        try:
            cumulative_fig = st.session_state.funnel.get_cumulative_chart(selected_kpi)
            st.plotly_chart(cumulative_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating cumulative chart: {str(e)}")

    left_col, right_col = st.columns([0.5, 0.5])
    with left_col:
        # Display cdf chart
        try:
            cdf_fig = st.session_state.funnel.get_cdf_chart(selected_kpi)
            st.plotly_chart(cdf_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating cdf chart: {str(e)}")
    with right_col:
        # display pdf chart
        try:
            pdf_fig = st.session_state.funnel.get_pdf_chart(selected_kpi)
            st.plotly_chart(pdf_fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating pdf chart: {str(e)}")

else:
    st.warning(
        "No KPI nodes found in the collection. Please add KPI nodes in the Funnel Builder."
    )
