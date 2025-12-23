import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide")
st.title("Page 1: Multiline Text Input")

# Initialize session state for text if it doesn't exist
if "text_content" not in st.session_state:
    st.session_state.text_content = ""

# Multiline text box
text_input = st.text_area(
    "Enter your text here:", st.session_state.text_content, height=300
)

# Save button
if st.button("Save Text"):
    st.session_state.text_content = text_input
    st.session_state.dataframe_content = pd.DataFrame(
        json.loads(st.session_state.text_content)
    )
    st.success("Text saved to session state!")

st.write("Current content in session state:")
st.code(st.session_state.text_content)
