import streamlit as st

def code_editor():
    """
    Text editor for pasted code.
    """
    return st.text_area(
        "Code Editor",
        value="",
        height=300,
        placeholder="# Paste your Python code here...",
    )
