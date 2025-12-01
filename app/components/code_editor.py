import streamlit as st
from backend.project_manager import get_full_path

try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except Exception:
    ACE_AVAILABLE = False


def _language_for_file(path: str) -> str:
    ext = (path or "").split(".")[-1].lower()
    return {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "java": "java",
        "go": "golang",
        "rb": "ruby",
        "c": "c_cpp",
        "cpp": "c_cpp",
    }.get(ext, "python")


def code_editor(project_state):
    """
    Text editor for pasted code. If a project file is selected, load its contents
    into the editor and keep in sync when the selection changes.
    """
    state = st.session_state.setdefault(
        "editor_state", {"project_name": None, "active_file": None, "content": ""}
    )

    active_file = project_state.get("active_file")
    project_name = project_state.get("project_name")

    # When a new file is selected, load it into the editor
    if active_file and (
        active_file != state.get("active_file")
        or project_name != state.get("project_name")
    ):
        try:
            with open(get_full_path(project_name, active_file), "r", encoding="utf-8") as f:
                state["content"] = f.read()
        except Exception as e:
            st.warning(f"Could not load {active_file}: {e}")
            state["content"] = ""
        state["active_file"] = active_file
        state["project_name"] = project_name

    widget_key = f"code_editor_{project_name}_{active_file}"

    # Prefer Ace editor if available for syntax + line numbers
    if ACE_AVAILABLE:
        language = _language_for_file(active_file or "")
        content = st_ace(
            value=state.get("content", ""),
            language=language,
            theme="monokai",
            key=widget_key,
            height=320,
            show_gutter=True,
            tab_size=4,
            wrap=False,
            auto_update=True,
            min_lines=10,
        )
    else:
        # Dark-themed fallback
        st.markdown(
            """
            <style>
            textarea[data-testid="stTextArea"] {
                font-family: Menlo, Consolas, monospace;
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 6px;
            }
            textarea[data-testid="stTextArea"]:focus {
                border-color: #6366f1;
                box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.35);
                outline: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        content = st.text_area(
            "Code Editor",
            value=state.get("content", ""),
            height=320,
            placeholder="# Paste your code here...",
            key=widget_key,
        )

    # Persist edits to session so reruns keep the typed code
    state["content"] = content
    return content
