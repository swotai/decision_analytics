import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from decision_analytics import Funnel, NodesCollection
from decision_analytics.plotting_utils.flowchart import (
    generate_funnel_chart_mermaid_code,
)

if "nodes_collection" not in st.session_state:
    st.session_state.nodes_collection = NodesCollection()
    st.session_state.funnel = Funnel(st.session_state.nodes_collection)

if "nodes_df" not in st.session_state:
    pass

st.title("Funnel Builder")

# Split the page into two columns
left_col, right_col = st.columns([0.6, 0.4])

# Backup table config:
# column_config={
#     "Name": st.column_config.TextColumn("Name", required=True),
#     "Long Name": st.column_config.TextColumn("Long Name"),
#     "Description": st.column_config.TextColumn("Description"),
#     "Value": st.column_config.NumberColumn("Value"),
#     "Value Low": st.column_config.NumberColumn("Value"),
#     "Value Mid": st.column_config.NumberColumn("Value"),
#     "Value High": st.column_config.NumberColumn("Value"),
#     "Format": st.column_config.TextColumn("Format"),
#     "Is KPI": st.column_config.CheckboxColumn(
#         "Is KPI", default=False, disabled=True
#     ),
#     "Input Type": st.column_config.TextColumn("Input Type", required=True),
# },


def update_df():
    st.session_state.nodes_df = pd.concat(
        [editable_input_df, editable_calc_df],
        ignore_index=True,
    )


def update_nodes_collection_from_df():
    st.session_state.nodes_json_str = st.session_state.nodes_df.to_json(
        orient="records"
    )

    try:
        # Update nodes collection
        st.session_state.nodes_collection.from_json_str(st.session_state.nodes_json_str)
        st.session_state.funnel = Funnel(st.session_state.nodes_collection)
        st.session_state.funnel.simulate()
        st.success("Funnel definition updated successfully!")

    except Exception as e:
        st.error(f"Error updating nodes collection: {str(e)}")


st.write(st.session_state)

with left_col:
    # Input Nodes Table
    st.subheader("Input Nodes")
    editable_input_df = st.data_editor(
        st.session_state.nodes_df[st.session_state.nodes_df["node_type"] == "input"],
        key="edited_input_df",
        num_rows="dynamic",
        width="stretch",
    )

    # Calculated Nodes Table
    st.subheader("Calculated Nodes")
    editable_calc_df = st.data_editor(
        st.session_state.nodes_df[
            st.session_state.nodes_df["node_type"] == "calculation"
        ],
        key="edited_calc_df",
        num_rows="dynamic",
        width="stretch",
    )

    if st.button("Refresh All Data", key="refresh_all"):
        update_df()
        update_nodes_collection_from_df()


# TODO: should we move mermaid code as a state within the funnel instance?
# Also add drag and zoom: https://github.com/mermaid-js/mermaid/issues/2162#issuecomment-1542542439
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
    kpi_col, refresh_col = st.columns([0.2, 0.8], vertical_alignment="bottom")

    with kpi_col:
        # Create a selectbox for KPI selection
        selected_kpi = st.selectbox(
            "Select KPI to display",
            options=[node.name for node in kpi_nodes],
            format_func=lambda x: st.session_state.nodes_collection.get_node(
                x
            ).long_name,
        )

    # with refresh_col:
    #     # Add refresh button
    #     if st.button("Refresh Calculation"):
    #         # Update the funnel calculations
    #         st.session_state.funnel.simulate()

    # Split the page into two columns
    left_col, right_col = st.columns([0.5, 0.5])
    with left_col:
        # Get and display tornado chart
        try:
            tornado_fig = st.session_state.funnel.get_tornado_chart(selected_kpi)
            st.plotly_chart(tornado_fig, width="stretch")
        except Exception as e:
            st.error(f"Error generating tornado chart: {str(e)}")

    with right_col:
        # Display cumulative chart
        try:
            cumulative_fig = st.session_state.funnel.get_cumulative_chart(selected_kpi)
            st.plotly_chart(cumulative_fig, width="stretch")
        except Exception as e:
            st.error(f"Error generating cumulative chart: {str(e)}")

    left_col, right_col = st.columns([0.5, 0.5])
    with left_col:
        # Display cdf chart
        try:
            cdf_fig = st.session_state.funnel.get_cdf_chart(selected_kpi)
            st.plotly_chart(cdf_fig, width="stretch")
        except Exception as e:
            st.error(f"Error generating cdf chart: {str(e)}")
    with right_col:
        # display pdf chart
        try:
            pdf_fig = st.session_state.funnel.get_pdf_chart(selected_kpi)
            st.plotly_chart(pdf_fig, width="stretch")
        except Exception as e:
            st.error(f"Error generating pdf chart: {str(e)}")
    pr = st.session_state.funnel.get_kpi_negative_probability(selected_kpi)
    st.text(
        f"There is a {pr*100:.3g}% chance that the KPI {selected_kpi} will be negative"
    )
else:
    st.warning(
        "No KPI nodes found in the collection. Please add KPI nodes in the Funnel Builder."
    )
