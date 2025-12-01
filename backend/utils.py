import os
import uuid
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)


def save_temp_script(project_name: str, code: str) -> Path:
    """
    Saves the code into a temporary .py file under workspace/project_name/.tmp/.

    Returns:
        Path to the saved .py file.
    """
    project_dir = WORKSPACE_DIR / project_name
    tmp_dir = project_dir / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # unique filename
    filename = f"{uuid.uuid4().hex}.py"
    filepath = tmp_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    return filepath
