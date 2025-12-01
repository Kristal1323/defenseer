import streamlit as st

def code_editor():
    """
    Text editor for pasted code.
    """
    default_code = "# Paste your Python code here..."
    return st.text_area("Code Editor", default_code, height=300)
