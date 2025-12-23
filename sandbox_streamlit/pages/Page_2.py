import streamlit as st
import pandas as pd
import json

st.set_page_config(layout="wide")
st.title("Page 2: Editable DataFrame")

# Initialize session state for dataframe if it doesn't exist
if "dataframe_content" not in st.session_state:
    st.session_state.dataframe_content = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4],
            "col2": ["A", "B", "C", "D"],
            "col3": [True, False, True, False],
        }
    )

st.write("Edit the DataFrame below:")

edited_df = st.data_editor(st.session_state.dataframe_content, num_rows="dynamic")

if st.button("Save DataFrame"):
    st.session_state.dataframe_content = edited_df
    # save the edited_df to JSON string and store in text_content state
    st.session_state.text_content = json.dumps(edited_df.to_dict(orient="records"))
    st.success("DataFrame saved to session state!")

st.write("Current DataFrame in session state:")
st.dataframe(st.session_state.dataframe_content)
