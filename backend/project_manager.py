import os
import zipfile
from pathlib import Path
from typing import List, Dict
import shutil

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)


def create_project(name: str) -> Path:
    """
    Creates a new project directory under workspace/.
    Returns the project path.
    """
    project_path = WORKSPACE_DIR / name
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path


def save_uploaded_files(project_name: str, files: List) -> List[Path]:
    """
    Saves multiple uploaded .py files into the project directory.
    Returns list of saved file paths.
    """
    project_path = create_project(project_name)
    saved_paths = []

    for file in files:
        filepath = project_path / file.name
        with open(filepath, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(filepath)

    return saved_paths


def save_uploaded_zip(project_name: str, zip_file) -> Path:
    """
    Saves and extracts a ZIP file into the project directory,
    preserving folder structure.
    """
    project_path = create_project(project_name)

    zip_path = project_path / zip_file.name
    with open(zip_path, "wb") as f:
        f.write(zip_file.getbuffer())

    # Extract zip contents
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(project_path)

    return project_path


def list_project_files(project_name: str) -> List[str]:
    """
    Returns a list of source files inside the project's folder structure.
    Paths are returned relative to project root.
    """
    project_path = WORKSPACE_DIR / project_name
    if not project_path.exists():
        return []

    allowed_exts = {".py", ".js", ".ts", ".java", ".go", ".rb", ".c", ".cpp"}
    files = []
    for file in project_path.rglob("*"):
        if not file.is_file():
            continue
        # Skip temp files under .tmp
        rel_parts = file.relative_to(project_path).parts
        if any(part == ".tmp" for part in rel_parts):
            continue
        # Skip macOS resource fork files from zips
        if file.name.startswith("._") or "__MACOSX" in rel_parts:
            continue

        if file.suffix.lower() in allowed_exts:
            rel = file.relative_to(project_path)
            files.append(str(rel))

    return sorted(files)


def clean_temp_files(project_name: str):
    """
    Removes transient files under workspace/<project>/.tmp.
    Safe to call repeatedly; ignores errors.
    """
    tmp_dir = WORKSPACE_DIR / project_name / ".tmp"
    if not tmp_dir.exists():
        return
    try:
        for f in tmp_dir.glob("*.py"):
            try:
                f.unlink()
            except Exception:
                pass
    except Exception:
        pass


def delete_project(project_name: str):
    """
    Removes an entire project directory under workspace/.
    Intended for resets/cleanup after uploads.
    """
    project_path = WORKSPACE_DIR / project_name
    try:
        shutil.rmtree(project_path)
    except FileNotFoundError:
        pass
    except Exception:
        # ignore cleanup errors
        pass


def get_full_path(project_name: str, relative_path: str) -> Path:
    """
    Converts a relative file path (from tree view) into a full absolute path.
    """
    return WORKSPACE_DIR / project_name / relative_path
