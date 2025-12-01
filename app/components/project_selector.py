import streamlit as st
from backend.project_manager import (
    create_project,
    save_uploaded_files,
    save_uploaded_zip,
    list_project_files,
    clean_temp_files,
    delete_project,
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

    # Clear workspace on demand (placed near create/load)
    if st.button("🧹 Clear workspace (delete project files)"):
        delete_project(project_name)
        state["active_file"] = None
        # Clear editor content as well
        st.session_state.pop("editor_state", None)
        st.rerun()

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
    st.write(f"### Project Files — `{project_name}`")

    file_list = list_project_files(project_name)
    if not file_list:
        st.info("No source files found in this project yet.")
        return state

    # Build a proper folder-aware tree for display
    def build_tree(paths):
        tree = {}
        for p in paths:
            parts = p.split("/")
            node = tree
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    node.setdefault("_files", set()).add(part)
                else:
                    node = node.setdefault(part, {})
        return tree

    def render_tree(node, prefix=""):
        lines = []
        dirs = sorted(k for k in node.keys() if k != "_files")
        for d in dirs:
            lines.append(f"{prefix}📁 {d}")
            lines.extend(render_tree(node[d], prefix + "    "))
        files = sorted(node.get("_files", []))
        for f in files:
            lines.append(f"{prefix}└─ {f}")
        return lines

    tree = build_tree(file_list)
    tree_entries = [f"📁 {project_name}"] + render_tree(tree, "    ")
    st.markdown("```\n" + "\n".join(tree_entries) + "\n```")

    # Build simple labels for the radio list using full relative paths
    labels = {}
    sorted_files = sorted(file_list)
    for path in sorted_files:
        labels[path] = f"{project_name}/{path}"

    active_file = st.radio(
        "Select a file to open:",
        options=sorted_files,
        index=sorted_files.index(state["active_file"]) if state["active_file"] in sorted_files else 0,
        format_func=lambda p: labels.get(p, p),
    )

    state.update({"project_name": project_name, "active_file": active_file})
    return state
