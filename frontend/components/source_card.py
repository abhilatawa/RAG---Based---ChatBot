import streamlit as st
from utils.session_state import ROLE_COLORS


def render_sources(sources: list):
    if not sources:
        return

    st.markdown(
        "<div style='font-size:12px; color:gray; margin:8px 0 4px; font-weight:600;'>"
        "📎 Sources</div>",
        unsafe_allow_html=True,
    )
    for src in sources:
        dept  = src.get("department", "general")
        color = ROLE_COLORS.get(dept, "#374151")
        score = int(src.get("score", 0) * 100)

        with st.expander(f"📄  {src['filename']}  ·  Page {src['page']}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(
                    f"<span style='font-size:11px; background:{color}15; color:{color};"
                    f"border:1px solid {color}40; border-radius:20px; padding:2px 10px;"
                    f"font-weight:700; letter-spacing:.05em;'>{dept.upper()}</span>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"<span style='font-size:11px; color:gray;'>relevance: {score}%</span>",
                    unsafe_allow_html=True,
                )
