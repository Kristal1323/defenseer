import streamlit as st
from backend.project_manager import (
    create_project,
    save_uploaded_files,
    save_uploaded_zip,
    list_project_files,
    clean_temp_files,
)

def project_selector():
    st.write("Create or select a project:")
    project_name = st.text_input("Project Name", value="default_project")

    # Clean temp files on each render to avoid clutter from previous runs
    clean_temp_files(project_name)

    if st.button("Create Project"):
        create_project(project_name)
        st.success(f"Project '{project_name}' created.")

    st.divider()
    st.write("### Upload Code")

    # Upload .py files
    uploaded_files = st.file_uploader(
        "Upload Python files (.py)",
        type=["py"],
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
        st.info("No Python files found in this project yet.")
        return {"project_name": project_name, "active_file": None}

    active_file = st.selectbox(
        "Select a file to run/analyze:",
        file_list,
        index=0,
    )

    return {
        "project_name": project_name,
        "active_file": active_file,
    }
