"""
backend/ai_fixer.py
Secure code auto-fixer using OpenAI Chat Completions API.

Place your API key in .streamlit/secrets.toml:
  [openai]
  api_key = "YOUR_API_KEY"
or set env var OPENAI_API_KEY.
"""

import os
import streamlit as st
from openai import OpenAI

OPENAI_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are a security-focused code rewriting assistant.
Your job is to rewrite ONLY the given vulnerable code block and fix the vulnerability.

Rules:
- Preserve original program logic.
- Remove the vulnerability entirely.
- Do NOT add new functionality.
- Do NOT rewrite unrelated code.
- Do NOT add explanations.
- Respond ONLY with the rewritten code block.
"""


def _get_api_key():
    """Fetch API key from Streamlit secrets or environment, if present."""
    key = None
    try:
        if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
            key = st.secrets["openai"]["api_key"]
    except Exception:
        # st.secrets may not be configured; fallback to env
        pass

    if not key:
        key = os.environ.get("OPENAI_API_KEY")
    return key


def generate_fix(vuln_description: str, code_snippet: str) -> str:
    """
    Calls OpenAI API to rewrite insecure code into a safe version.
    """
    api_key = _get_api_key()
    if not api_key:
        return "[AI fix failed: OpenAI API key missing. Add it to .streamlit/secrets.toml or OPENAI_API_KEY env var.]"

    if not code_snippet or not str(code_snippet).strip():
        return "[AI fix failed: No vulnerable code snippet provided.]"

    client = OpenAI(api_key=api_key)

    prompt = f"""
    The following code contains a security vulnerability.

    Description:
    {vuln_description}

    Vulnerable Code:
    {code_snippet}

    Rewrite ONLY this block to eliminate the vulnerability.
    Return only the fixed code block.
    """

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=300,
        )
        if not resp.choices:
            return "[AI fix failed: no completion returned]"
        content = resp.choices[0].message.content or ""
        content = content.strip()
        if not content:
            return "[AI fix failed: empty completion]"
        return content
    except Exception as e:
        return f"[AI fix failed: {e}]"
