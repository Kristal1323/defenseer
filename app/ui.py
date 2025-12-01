import streamlit as st
import sys
from pathlib import Path

# Ensure project root is on sys.path so `app.*` imports work even when cwd is app/
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components.project_selector import project_selector
from app.components.code_editor import code_editor
from app.components.output_console import output_console
from app.components.vulnerability_panel import vulnerability_panel
from app.components.fix_suggestions import fix_suggestions

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

    # Fullscreen editor mode
    if st.session_state.get("show_editor_fullscreen"):
        st.subheader("🖥 Code Editor (Fullscreen)")
        pasted_code = code_editor(project_state, full_screen=True, key_prefix="full_")
        output_console(project_state, pasted_code)
        if st.button("Close fullscreen editor"):
            st.session_state["show_editor_fullscreen"] = False
            st.rerun()
        st.stop()

    st.subheader("🖥 Code Editor")
    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("Open fullscreen editor"):
            st.session_state["show_editor_fullscreen"] = True
            st.rerun()
    with cols[1]:
        run_now = st.button("▶ Run Code", use_container_width=True)

    pasted_code = code_editor(project_state, full_screen=False, key_prefix="main_")
    output_console(project_state, pasted_code, run_triggered=run_now, show_button=False)

    st.subheader("🔍 Vulnerability Analysis")
    vulnerability_panel(project_state, pasted_code)
    st.subheader("🧠 AI Fix Suggestions")
    fix_suggestions(project_state)


if __name__ == "__main__":
    main()
