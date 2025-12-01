import streamlit as st
from components.project_selector import project_selector
from components.code_editor import code_editor
from components.output_console import output_console
from components.vulnerability_panel import vulnerability_panel
from components.fix_suggestions import fix_suggestions

st.set_page_config(
    page_title="DefenSeer",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    st.title("🛡️ DefenSeer — AI-Augmented Secure Code Runner")

    with st.sidebar:
        st.header("📂 Projects")
        project_state = project_selector()

    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Code Editor")
        pasted_code = code_editor(project_state)

        st.subheader("▶️ Program Output")
        output_console(project_state, pasted_code)

    with col2:
        st.subheader("🔍 Vulnerability Analysis")
        vulnerability_panel(project_state, pasted_code)

    st.subheader("🧠 Suggested Fixes (AI)")
    fix_suggestions(project_state)

if __name__ == "__main__":
    main()
