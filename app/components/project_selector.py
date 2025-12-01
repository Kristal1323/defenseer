import streamlit as st
from backend.project_manager import (
    create_project,
    save_uploaded_files,
    save_uploaded_zip,
    list_project_files,
    clean_temp_files,
)


def project_selector():
    """
    Sidebar project manager with multi-file support and simple tree view.
    Keeps project + active file in session so state persists across reruns.
    """
    state = st.session_state.setdefault(
        "project_state", {"project_name": "default_project", "active_file": None}
    )

    st.write("Create or select a project:")
    project_name = st.text_input(
        "Project Name",
        value=state.get("project_name", "default_project"),
        key="project_name_input",
    )

    # Clean temp files on each render to avoid clutter from previous runs
    clean_temp_files(project_name)

    if st.button("Create/Load Project"):
        create_project(project_name)
        st.success(f"Project '{project_name}' ready.")
        state["project_name"] = project_name

    st.divider()
    st.write("### Upload Code")

    # Upload multiple source files
    uploaded_files = st.file_uploader(
        "Upload source files",
        type=["py", "js", "ts", "java", "go", "rb", "c", "cpp"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        save_uploaded_files(project_name, uploaded_files)
        st.success(f"Uploaded {len(uploaded_files)} files.")

    # Upload folder as .zip
    uploaded_zip = st.file_uploader("Upload entire project folder (.zip)", type=["zip"])
    if uploaded_zip:
        save_uploaded_zip(project_name, uploaded_zip)
        st.success("ZIP extracted successfully.")

    st.divider()
    st.write("### Project Files")

    file_list = list_project_files(project_name)
    if not file_list:
        st.info("No source files found in this project yet.")
        return state

    # Simple tree-like view via relative paths
    active_file = st.radio(
        "Select a file to open:",
        options=file_list,
        index=file_list.index(state["active_file"]) if state["active_file"] in file_list else 0,
        format_func=lambda p: p,
    )

    state.update({"project_name": project_name, "active_file": active_file})
    return state
