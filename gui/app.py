import streamlit as st
from decision_analytics import NodesCollection, Node, CalculatedNode


def create_node_builder_app():
    st.title("Decision Analytics Node Builder")

    # Initialize session state
    if "nodes_collection" not in st.session_state:
        st.session_state.nodes_collection = NodesCollection()

    # Sidebar for adding nodes
    with st.sidebar:
        st.header("Add New Node")
        node_type = st.selectbox("Node Type", ["Input Node", "Calculated Node"])

        # Common fields
        name = st.text_input("Node Name (short)")
        long_name = st.text_input("Node Long Name (optional)")
        format_str = st.text_input("Format String (e.g., '.2%')", value="")

        if node_type == "Input Node":
            value = st.number_input("Initial Value", value=0.0)
            # Optional percentiles
            use_percentiles = st.checkbox("Add Percentiles")
            if use_percentiles:
                p10 = st.number_input("10th Percentile", value=0.0)
                p50 = st.number_input("50th Percentile", value=0.0)
                p90 = st.number_input("90th Percentile", value=0.0)
                value_percentiles = (p10, p50, p90)
            else:
                value_percentiles = None

        else:  # Calculated Node
            definition = st.text_input("Definition (e.g., 'node1 * node2')")
            is_kpi = st.checkbox("Is KPI")

        if st.button("Add Node"):
            try:
                if node_type == "Input Node":
                    node_dict = {
                        "name": name,
                        "long_name": long_name,
                        "value": value,
                        "format_str": format_str,
                        "input_type": "input",
                    }
                    if value_percentiles:
                        node_dict["value_percentiles"] = value_percentiles
                else:
                    node_dict = {
                        "name": name,
                        "long_name": long_name,
                        "definition": definition,
                        "format_str": format_str,
                        "input_type": "calculation",
                        "is_kpi": is_kpi,
                    }

                st.session_state.nodes_collection.add_nodes([node_dict])
                st.success(f"Added {node_type.lower()}: {name}")
            except Exception as e:
                st.error(f"Error adding node: {str(e)}")

    # Main area - Display current nodes
    st.header("Current Nodes")

    # Input Nodes
    st.subheader("Input Nodes")
    input_nodes = st.session_state.nodes_collection.get_input_nodes()
    for node in input_nodes:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"Name: {node.name}")
        with col2:
            st.write(f"Value: {node.value}")
        with col3:
            if st.button("Edit", key=f"edit_{node.name}"):
                # Add edit functionality
                pass
        with col4:
            if st.button("Delete", key=f"delete_{node.name}"):
                st.session_state.nodes_collection.remove_node(node.name)
                st.experimental_rerun()

    # Calculated Nodes
    st.subheader("Calculated Nodes")
    calc_nodes = st.session_state.nodes_collection.get_calculated_nodes()
    for node in calc_nodes:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"Name: {node.name}")
        with col2:
            st.write(f"Definition: {node.definition}")
        with col3:
            if st.button("Edit", key=f"edit_{node.name}"):
                # Add edit functionality
                pass
        with col4:
            if st.button("Delete", key=f"delete_{node.name}"):
                st.session_state.nodes_collection.remove_node(node.name)
                st.experimental_rerun()

    # Display flowchart
    if len(st.session_state.nodes_collection.nodes) > 0:
        st.header("Flowchart")
        from decision_analytics.plotting_utils.flowchart import (
            generate_funnel_chart_mermaid_code,
        )

        mermaid_code = generate_funnel_chart_mermaid_code(
            st.session_state.nodes_collection
        )
        st.markdown(mermaid_code)


if __name__ == "__main__":
    create_node_builder_app()
