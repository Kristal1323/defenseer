import streamlit as st
from backend.runner import run_code_sandbox
from backend.project_manager import get_full_path


def output_console(project_state, pasted_code):
    """
    Executes either:
    - the selected project file, or
    - the pasted code, if no file is selected.

    Displays stdout, stderr, and execution status.
    """
    project_name = project_state["project_name"]
    active_file = project_state["active_file"]

    # UI Button
    if st.button("▶ Run Code", use_container_width=True):
        st.write("Running code...")

        # If a file is selected → run that file
        if active_file:
            file_path = get_full_path(project_name, active_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return
        else:
            code = pasted_code

        # Run sandbox
        result = run_code_sandbox(project_name, code)

        # Display results
        if not result["success"]:
            st.error(f"Error: {result.get('error', 'Unknown error')}")
            return

        st.success(f"Execution completed (exit code {result['exit_code']})")

        if result["stdout"]:
            st.code(result["stdout"], language="text")

        if result["stderr"]:
            st.error("Errors:")
            st.code(result["stderr"], language="text")
