"""
backend/code_patcher.py

Patch helpers for applying AI-generated fixes to the original source.
The AI may return a snippet that does not exactly match Bandit's snippet,
so we fall back to a fuzzy, line-based replacement when direct matching fails.
"""

import difflib
from typing import List, Tuple


def _normalize_block(block: str) -> str:
    """Trim common leading/trailing whitespace for comparison."""
    return "\n".join(line.rstrip() for line in block.strip().splitlines())


def _indent_block(block: str, indent: str) -> str:
    """Apply leading indent to every non-empty line."""
    result_lines = []
    for line in block.splitlines():
        if line.strip():
            result_lines.append(f"{indent}{line}")
        else:
            result_lines.append(line)
    return "\n".join(result_lines)


def _find_fuzzy_span(source_lines: List[str], target_lines: List[str]) -> Tuple[int, int, float]:
    """
    Find the span in source_lines that best matches target_lines using difflib.
    Returns (start_idx, end_idx, score). Higher score is better.
    """
    best = (-1, -1, 0.0)
    tlen = len(target_lines)
    if tlen == 0:
        return best

    for i in range(0, len(source_lines) - tlen + 1):
        window = source_lines[i : i + tlen]
        score = difflib.SequenceMatcher(
            None,
            "\n".join(window),
            "\n".join(target_lines),
        ).ratio()
        if score > best[2]:
            best = (i, i + tlen, score)
    return best


def apply_patch_to_source(source_code: str, old_block: str, new_block: str) -> str:
    """
    Replace old_block with new_block inside source_code.

    Strategy:
    1) Exact replace on the trimmed block.
    2) Fuzzy line-based replace using difflib best match (if reasonably high score).
    """
    old_block_norm = _normalize_block(old_block)
    new_block_norm = _normalize_block(new_block)

    # If we don't have something meaningful to replace with, leave source untouched.
    if not old_block_norm or not new_block_norm:
        return source_code

    # Fast path: exact match
    if old_block_norm in source_code:
        return source_code.replace(old_block_norm, new_block_norm)

    # Fuzzy match: try to find closest span of lines
    source_lines = source_code.splitlines()
    target_lines = old_block_norm.splitlines()
    start, end, score = _find_fuzzy_span(source_lines, target_lines)

    # Require a reasonable similarity to avoid bad replacements
    if start == -1 or score < 0.5:
        return source_code

    # Preserve indentation based on the first line of the matched span
    matched_first_line = source_lines[start]
    indent = matched_first_line[: len(matched_first_line) - len(matched_first_line.lstrip())]
    patched_block = _indent_block(new_block_norm, indent)

    patched_lines = source_lines[:start] + patched_block.splitlines() + source_lines[end:]
    return "\n".join(patched_lines)
