import streamlit as st
from backend.ai_fixer import generate_fix
from backend.code_patcher import apply_patch_to_source
from backend.project_manager import get_full_path
from backend.diff_utils import generate_diff


def fix_suggestions(project_state):
    """
    Generate AI-powered fixes for Bandit findings.
    Requires a prior security scan so we have issue descriptions/snippets.
    """
    issues = st.session_state.get("scan_results") or []
    has_issues = bool(issues)

    if not has_issues:
        st.info("Run a security scan first to generate fix suggestions.")

    project_name = project_state.get("project_name")
    active_file = project_state.get("active_file")
    file_path = get_full_path(project_name, active_file) if active_file else None

    ai_results = st.session_state.setdefault("ai_fix_results", {})

    if st.button("⚙️ Generate AI Fixes", disabled=not has_issues):
        with st.spinner("Requesting AI fixes..."):
            ai_results.clear()
            for idx, issue in enumerate(issues):
                code_snippet = (issue.get("code") or "").strip()
                ai_results[idx] = generate_fix(issue.get("text", ""), code_snippet)

    if not ai_results:
        return

    st.markdown("### AI Fix Suggestions")
    for idx, issue in enumerate(issues):
        if idx not in ai_results:
            continue

        code_snippet = (issue.get("code") or "").strip()
        fixed_block = ai_results[idx]

        st.markdown("---")
        st.markdown(f"**Rule:** {issue.get('test_id')} — {issue.get('test_name')}")
        st.markdown(f"**Location:** `{issue.get('filename','?')}:{issue.get('line_number','?')}`")
        st.markdown(f"**Description:** {issue.get('text','(no description)')}")

        if code_snippet:
            st.markdown("**Vulnerable code:**")
            st.code(code_snippet, language="python")

        if not fixed_block or fixed_block.strip().startswith("[AI fix failed"):
            st.warning(f"AI fix unavailable for this issue: {fixed_block or 'no output'}")
            continue

        st.markdown("**AI-proposed fix:**")
        st.code(fixed_block, language="python")

        # Side-by-side preview
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Original (targeted snippet):**")
            st.code(code_snippet, language="python")
        with cols[1]:
            st.markdown("**Secure rewrite:**")
            st.code(fixed_block, language="python")

        # Diff view + patched file preview
        if code_snippet and file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()
                patched = apply_patch_to_source(source, code_snippet, fixed_block)
                if patched != source:
                    st.markdown("**Diff (before → after):**")
                    st.code(generate_diff(source, patched), language="diff")
                    st.markdown("**Patched file preview:**")
                    st.code(patched, language="python")
                else:
                    st.warning("AI fix could not be aligned with the source file (snippet not found).")
            except Exception as e:
                st.warning(f"Could not build patched preview: {e}")
