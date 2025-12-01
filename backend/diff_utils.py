# backend/diff_utils.py
import difflib

def generate_diff(original: str, fixed: str) -> str:
    """
    Creates a unified diff string for display in UI.
    """
    diff = difflib.unified_diff(
        original.splitlines(),
        fixed.splitlines(),
        fromfile="before.py",
        tofile="after.py",
        lineterm=""
    )
    return "\n".join(diff)
