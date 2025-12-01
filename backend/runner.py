import subprocess
import sys
import resource
import signal
import platform
import shutil
import tempfile
from pathlib import Path
from backend.utils import save_temp_script


class SandboxError(Exception):
    """Raised when sandboxed execution fails."""
    pass


def _copy_project_to_temp(project_name: str) -> Path:
    """
    Copy the entire project folder to a temp directory, skipping temp/artifact files.
    """
    src = Path("workspace") / project_name
    if not src.exists():
        raise SandboxError(f"Project '{project_name}' not found.")

    tmp_dir = Path(tempfile.mkdtemp(prefix=f"{project_name}_"))
    ignore = shutil.ignore_patterns(".tmp", "__pycache__", ".git", "*.pyc")
    shutil.copytree(src, tmp_dir, dirs_exist_ok=True, ignore=ignore)
    return tmp_dir


def _limit_resources():
    """
    Apply resource limits for sandboxed execution:
    - Limit CPU time
    - Limit memory (Linux only, fallback for macOS)
    """
    # CPU time limit (works on all platforms)
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))

    system = platform.system()

    # macOS does NOT support RLIMIT_AS -> fallback to RLIMIT_DATA
    if system == "Darwin":
        try:
            resource.setrlimit(
                resource.RLIMIT_DATA,
                (200 * 1024 * 1024, 200 * 1024 * 1024)  # 200MB heap limit
            )
        except Exception:
            # If RLIMIT_DATA fails, silently skip memory limit
            pass

    # Linux → use RLIMIT_AS for full address space limit
    else:
        try:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (200 * 1024 * 1024, 200 * 1024 * 1024)  # 200MB memory limit
            )
        except Exception:
            pass


def run_code_sandbox(project_name: str, code: str, main_rel_path: str = None, timeout: int = 3):
    """
    Executes Python code safely inside a restricted subprocess.
    If main_rel_path is provided, copies the entire project to a temp folder
    and executes that file with limited resources.
    Returns:
        dict containing stdout, stderr, exit_code, and errors.
    """
    tmp_dir = None
    filepath = None
    cwd = None

    try:
        if main_rel_path:
            # Multi-file: copy project to temp and run selected file
            tmp_dir = _copy_project_to_temp(project_name)
            main_path = tmp_dir / main_rel_path
            if not main_path.exists():
                raise SandboxError(f"Main file not found in project copy: {main_rel_path}")
            cmd = [sys.executable, str(main_path)]
            cwd = str(main_path.parent)
        else:
            # Single snippet: save to temp script
            filepath = save_temp_script(project_name, code)
            cmd = [sys.executable, str(filepath)]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=_limit_resources,  # resource sandbox
            text=True,
            cwd=cwd,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "error": "Execution timed out",
                "stdout": "",
                "stderr": ""
            }

        exit_code = process.returncode

        return {
            "success": True,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "file": str(main_rel_path or filepath)
        }

    except Exception as e:
        raise SandboxError(f"Sandbox execution failed: {e}")
    finally:
        # Clean up temp artifacts
        if filepath:
            try:
                Path(filepath).unlink(missing_ok=True)
            except Exception:
                pass
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
