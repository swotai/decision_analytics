import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Page 3: Dataframe Editor")

# Initialize session state for page 3 dataframe
if "page3_df" not in st.session_state:
    st.session_state.page3_df = pd.DataFrame(
        {
            "type": ["input", "input", "calculation", "calculation"],
            "Name": ["volume", "rate", "revenue", "profit"],
            "value": [100, 0.5, 50, 25],
        }
    )


def update_dataframe():
    """Updates the session state dataframe with the edited data."""
    st.session_state.page3_df = st.session_state.edited_input_df.copy()
    st.session_state.page3_df = st.session_state.edited_output_df.copy()


st.markdown("## Input Data")
edited_input_df = st.data_editor(
    st.session_state.page3_df[st.session_state.page3_df["type"] == "input"],
    key="edited_input_df",
    num_rows="dynamic",
)

st.markdown("## Output Data")
edited_output_df = st.data_editor(
    st.session_state.page3_df[st.session_state.page3_df["type"] == "calculation"],
    key="edited_output_df",
    num_rows="dynamic",
)

if st.button("Update"):
    # This currently overwrites the entire dataframe.
    # A more robust solution would merge changes from both edited_input_df and edited_output_df
    st.session_state.page3_df = pd.concat(
        [edited_input_df, edited_output_df], ignore_index=True
    )
    st.success("DataFrame updated!")

st.markdown("## Current Session State DataFrame (Full)")
st.dataframe(st.session_state.page3_df, use_container_width=True)
