import streamlit as st
import plotly.graph_objects as go

st.title("Charting")

# Add refresh button
if st.button("Refresh"):
    # Update the funnel calculations
    st.session_state.funnel.simulate()

# Get KPI nodes
kpi_nodes = st.session_state.nodes_collection.get_kpi_nodes()

if kpi_nodes:
    # Create a selectbox for KPI selection
    selected_kpi = st.selectbox(
        "Select KPI to display",
        options=[node.name for node in kpi_nodes],
        format_func=lambda x: st.session_state.nodes_collection.get_node(x).long_name,
    )

    # Get and display tornado chart
    try:
        tornado_fig = st.session_state.funnel.get_tornado_chart(selected_kpi)
        st.plotly_chart(tornado_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error generating tornado chart: {str(e)}")
else:
    st.warning(
        "No KPI nodes found in the collection. Please add KPI nodes in the Funnel Builder."
    )
