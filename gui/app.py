import streamlit as st
import json
from decision_analytics import NodesCollection, Funnel

# Initialize session state for nodes collection if it doesn't exist
if "nodes_collection" not in st.session_state:
    st.session_state.nodes_collection = NodesCollection()
    st.session_state.funnel = Funnel(st.session_state.nodes_collection)


def update_nodes_collection():
    """Update the funnel with the current nodes collection"""
    st.session_state.funnel = Funnel(st.session_state.nodes_collection)
    st.session_state.funnel.simulate()


st.set_page_config(page_title="Decision Analytics", layout="wide")
st.title("Decision Analytics")

# Create pages directory if it doesn't exist
