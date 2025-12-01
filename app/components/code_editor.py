import streamlit as st

def code_editor():
    """
    Placeholder for code editor input.
    Will later support file upload + text editor + syntax highlighting.
    """
    default_code = "# Paste your Python code here..."
    code = st.text_area("Code Editor", default_code, height=300)
    return code
