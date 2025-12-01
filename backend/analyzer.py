import json
import subprocess
import sys
from pathlib import Path
from backend.utils import save_temp_script
from backend.project_manager import get_full_path


class BanditError(Exception):
    """Raised when Bandit analysis fails."""
    pass


def extract_json_from_output(stdout: str, stderr: str):
    """
    Bandit sometimes prints JSON to stdout OR stderr depending on OS,
    and may prepend warnings before the JSON.

    This function extracts the JSON object from either stream.
    """
    for stream in (stdout, stderr):
        first_brace = stream.find("{")
        if first_brace != -1:
            return stream[first_brace:]

    # Nothing found → show stderr for debugging
    raise BanditError(
        f"No JSON found in Bandit output.\nSTDERR was:\n{stderr}"
    )


def run_bandit_on_code(project_name: str, code: str):
    temp_path = save_temp_script(project_name, code)
    return run_bandit_on_file(temp_path)


def run_bandit_on_file(file_path: Path):
    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
        str(file_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
    except Exception as e:
        raise BanditError(f"Bandit execution failed: {e}")

    if result.returncode not in (0, 1):
        raise BanditError(f"Bandit scan failed with stderr:\n{result.stderr}")

    # ----- FIX: Extract JSON from stdout OR stderr -----
    try:
        json_str = extract_json_from_output(result.stdout, result.stderr)
        bandit_json = json.loads(json_str)
    except Exception as e:
        raise BanditError(f"Failed to parse Bandit JSON output: {e}")

    return parse_bandit_results(bandit_json)


def parse_bandit_results(bandit_json: dict):
    issues = []

    for issue in bandit_json.get("results", []):
        issues.append({
            "filename": issue.get("filename"),
            "line_number": issue.get("line_number"),
            "severity": issue.get("issue_severity"),
            "confidence": issue.get("issue_confidence"),
            "text": issue.get("issue_text"),
            "code": issue.get("code", "").strip(),
            "test_id": issue.get("test_id"),
            "test_name": issue.get("test_name"),
        })

    return issues
