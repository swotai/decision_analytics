import json

import pandas as pd
import streamlit as st

from decision_analytics import Funnel, NodesCollection

if "nodes_collection" not in st.session_state:
    st.session_state.nodes_collection = NodesCollection()
    st.session_state.funnel = Funnel(st.session_state.nodes_collection)

st.title("Nodes JSON Editor")
st.write(st.session_state)

if "nodes_json_str" in st.session_state:
    current_json_str = st.session_state.nodes_json_str
else:
    current_json_str = []


def update_json():
    st.session_state.nodes_json_str = json_input


def update_funnel_from_json():
    """Updates the nodes collection from JSON"""
    try:
        # Try to parse the JSON to validate it
        if json_input is None:
            raise ValueError("JSON input cannot be empty")

        # Test with json loads to make sure json is valid
        try:
            json.loads(json_input)
        except ValueError as e:
            st.error(f"Invalid JSON: {str(e)}")

        # Update nodes collection
        st.session_state.nodes_collection.from_json_str(json_input)
        st.session_state.funnel = Funnel(st.session_state.nodes_collection)
        st.session_state.funnel.simulate()
        st.success("Funnel definition updated successfully!")

    except Exception as e:
        st.error(f"Error updating nodes collection: {str(e)}")


def update_df_from_json():
    if json_input is None:
        raise ValueError("No JSON loaded, cannot create nodes dataframe.")
    st.session_state.nodes_df = pd.DataFrame(json.loads(json_input))
    # st.success("Funnel table updated successfully!")


# Create a text area for JSON editing
json_input = st.text_area(
    "Edit Nodes Collection JSON here. The nodes collection will be updated automatically",
    value=current_json_str,
    height=600,
    # on_change=update_df_and_funnel,
)

# # Add update button
if st.button("Update"):
    update_json()
    update_funnel_from_json()
    update_df_from_json()

# TODO:
# On change of JSON field, do two things:
# Update dataframe session state for dataframe viewing
# update funnel and run simulate
