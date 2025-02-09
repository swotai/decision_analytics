import streamlit as st
from streamlit_elements import (
    elements,
    dashboard,
    mui,
    html,
    nivo,
    editor,
    media,
    lazy,
    sync,
    event,
)
from decision_analytics import NodesCollection
import uuid

# Initialize session state
if "nodes" not in st.session_state:
    st.session_state.nodes = []
if "edges" not in st.session_state:
    st.session_state.edges = []
if "nodes_collection" not in st.session_state:
    st.session_state.nodes_collection = NodesCollection()


def create_node_builder_app():
    st.title("Decision Analytics Node Builder")

    # Sidebar controls
    with st.sidebar:
        st.header("Add New Node")
        node_type = st.selectbox("Node Type", ["Input Node", "Calculated Node"])

        # Node creation form
        with st.form("node_form"):
            name = st.text_input("Node Name")
            if node_type == "Input Node":
                value = st.number_input("Value", value=0.0)
                format_str = st.text_input("Format String", value=".2f")
            else:
                format_str = st.text_input("Format String", value=".2f")

            submitted = st.form_submit_button("Add Node")
            if submitted:
                node_id = str(uuid.uuid4())
                new_node = {
                    "id": node_id,
                    "type": "default",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": name,
                        "node_type": node_type,
                        "value": value if node_type == "Input Node" else None,
                        "format_str": format_str,
                    },
                }
                st.session_state.nodes.append(new_node)

    # Main flow editor
    with elements("flow_editor"):
        # Custom styles for the flow
        styles = {
            ".react-flow__node": {
                "background": "#fff",
                "border": "1px solid #ddd",
                "borderRadius": "3px",
                "padding": "10px",
            }
        }

        # Layout configuration
        layout = {"name": "dagre", "rankDir": "TB", "nodesep": 50, "ranksep": 50}

        # Event handlers
        def handle_connect(params):
            source_id = params["source"]
            target_id = params["target"]
            edge_id = f"{source_id}-{target_id}"

            new_edge = {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "type": "smoothstep",
            }

            if new_edge not in st.session_state.edges:
                st.session_state.edges.append(new_edge)

        def handle_node_drag(event):
            node_id = event["id"]
            new_position = event["position"]

            for node in st.session_state.nodes:
                if node["id"] == node_id:
                    node["position"] = new_position
                    break

        # ReactFlow component
        with dashboard.Flow(
            nodes=st.session_state.nodes,
            edges=st.session_state.edges,
            style=styles,
            layout=layout,
            onConnect=handle_connect,
            onNodeDragStop=handle_node_drag,
            fitView=True,
        ):
            # Node types definition
            dashboard.Flow.Background(variant="dots", gap=12, size=1)

            # Controls
            dashboard.Flow.Controls()
            dashboard.Flow.MiniMap()

    # Display current node connections as text (for debugging)
    st.header("Current Connections")
    for edge in st.session_state.edges:
        st.write(f"Connection: {edge['source']} → {edge['target']}")

    # Convert to NodesCollection
    if st.button("Generate NodesCollection"):
        try:
            nodes_dict = {}
            calculated_nodes = []

            # First pass: create input nodes
            for node in st.session_state.nodes:
                if node["data"]["node_type"] == "Input Node":
                    nodes_dict[node["data"]["label"]] = {
                        "name": node["data"]["label"],
                        "value": node["data"]["value"],
                        "format_str": node["data"]["format_str"],
                        "input_type": "input",
                    }

            # Second pass: create calculated nodes
            for node in st.session_state.nodes:
                if node["data"]["node_type"] == "Calculated Node":
                    # Find incoming edges
                    incoming = [
                        e["source"]
                        for e in st.session_state.edges
                        if e["target"] == node["id"]
                    ]
                    # Create definition based on incoming nodes
                    node_names = [
                        n["data"]["label"]
                        for n in st.session_state.nodes
                        if n["id"] in incoming
                    ]
                    definition = " * ".join(
                        node_names
                    )  # Simple multiplication for demo

                    calculated_nodes.append(
                        {
                            "name": node["data"]["label"],
                            "definition": definition,
                            "format_str": node["data"]["format_str"],
                            "input_type": "calculation",
                        }
                    )

            # Create NodesCollection
            nc = NodesCollection()
            nc.add_nodes(list(nodes_dict.values()))
            nc.add_nodes(calculated_nodes)
            st.session_state.nodes_collection = nc
            st.success("NodesCollection generated successfully!")

        except Exception as e:
            st.error(f"Error generating NodesCollection: {str(e)}")


if __name__ == "__main__":
    create_node_builder_app()
