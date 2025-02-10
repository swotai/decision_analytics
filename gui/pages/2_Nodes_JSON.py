import streamlit as st
import json
from decision_analytics import Funnel

st.title("Nodes JSON Editor")

# Get current nodes collection as JSON
current_json = st.session_state.nodes_collection.to_json()

# Create a text area for JSON editing
json_input = st.text_area(
    "Edit Nodes Collection JSON",
    value=current_json,
    height=600,
    help="Edit the JSON directly. The nodes collection will be updated when you click 'Update'.",
)

# Add update button
if st.button("Update"):
    try:
        # Try to parse the JSON to validate it
        if json_input is None:
            raise ValueError("JSON input cannot be empty")
        json.loads(json_input)

        # Update the nodes collection
        st.session_state.nodes_collection.from_json(json_input)

        # Update the funnel
        st.session_state.funnel = Funnel(st.session_state.nodes_collection)
        st.session_state.funnel.simulate()

        st.success("Nodes collection updated successfully!")
    except ValueError as e:
        st.error(f"Invalid JSON: {str(e)}")
    except Exception as e:
        st.error(f"Error updating nodes collection: {str(e)}")
