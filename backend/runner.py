import subprocess
import sys
import resource
import signal
from pathlib import Path
from backend.utils import save_temp_script


class SandboxError(Exception):
    """Raised when sandboxed execution fails."""
    pass

def _limit_resources():
    """
    Apply resource limits for sandboxed execution:
    - Limit CPU time
    - Limit memory
    """
    # CPU time limit (seconds)
    resource.setrlimit(resource.RLIMIT_CPU, (2, 2))

    # Memory limit (bytes): 200MB
    resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, 200 * 1024 * 1024))


def run_code_sandbox(project_name: str, code: str, timeout: int = 3):
    """
    Executes Python code safely inside a restricted subprocess.
    Returns:
        dict containing stdout, stderr, exit_code, and errors.
    """
    filepath = save_temp_script(project_name, code)

    cmd = [sys.executable, str(filepath)]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=_limit_resources,     # resource sandbox
            text=True
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
            "file": str(filepath)
        }

    except Exception as e:
        raise SandboxError(f"Sandbox execution failed: {e}")
