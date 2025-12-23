import streamlit as st

st.set_page_config(layout="wide")
st.title("Streamlit Two-Page App")

st.markdown("## Main Page")
st.markdown("Welcome to the main page! Navigate to the other pages using the sidebar.")


st.markdown("## Extra Testing")
# 1. Initialize session state variables
if "value_a" not in st.session_state:
    st.session_state["value_a"] = 0
if "value_b" not in st.session_state:
    st.session_state["value_b"] = st.session_state["value_a"] * 2


# 2. Define the callback function
def update_b_from_a():
    """Updates 'value_b' based on the new 'value_a'."""
    # The new value of 'value_a' is available when the callback runs
    st.session_state["value_b"] = st.session_state["value_a"] * 2


def update_a_from_b():
    """Updates 'value_a' based on the new 'value_b'."""
    st.session_state["value_a"] = st.session_state["value_b"] / 2


# 3. Use a widget with a callback
st.number_input(
    "Enter Value A",
    key="value_a",  # Links the widget to st.session_state['value_a']
    on_change=update_b_from_a,  # Function to call when value changes
)

# 4. Display the results
st.write(f"Value A is: {st.session_state['value_a']}")
st.write(f"Value B (derived) is: {st.session_state['value_b']}")

# An independent input for demonstration
st.number_input(
    "Value B can also be manually changed here:",
    key="value_b",
    on_change=update_a_from_b,
)
