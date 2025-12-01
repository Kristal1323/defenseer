import json
import subprocess
import re
import os


class BanditError(Exception):
    pass


def extract_json_block(text: str):
    """
    Extracts the last JSON object from arbitrary text.
    Bandit sometimes prints INFO logs before JSON, so we find the LAST {...} block.
    """
    json_matches = list(re.finditer(r"\{.*\}", text, re.DOTALL))
    if not json_matches:
        raise BanditError("No JSON block found in Bandit output.")

    # Use LAST match (Bandit prints logs before JSON)
    json_text = json_matches[-1].group(0)
    return json_text


def run_bandit_on_file(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    cmd = ["bandit", "-f", "json", path]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True
        )
    except Exception as e:
        raise BanditError(f"Failed to run Bandit: {e}")

    raw_output = result.stdout + "\n" + result.stderr

    try:
        json_block = extract_json_block(raw_output)
        data = json.loads(json_block)
    except Exception as e:
        raise BanditError(f"Failed to parse Bandit JSON output: {e}")

    # Extract results list
    issues = data.get("results", [])
    return issues
