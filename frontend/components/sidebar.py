import asyncio
import streamlit as st
from utils.session_state import ROLE_COLORS, ROLE_LABELS, ROLE_DESCRIPTIONS, clear_user
from utils.api_client import APIClient


def render_sidebar():
    with st.sidebar:
        # Logo / brand
        st.markdown(
            """
            <div style='text-align:center; padding: 8px 0 16px;'>
                <div style='font-size:32px;'>🏦</div>
                <div style='font-weight:700; font-size:18px; margin-top:4px;'>FinSolve</div>
                <div style='font-size:11px; color:gray; letter-spacing:.08em;
                            text-transform:uppercase;'>AI Assistant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        role  = st.session_state.get("role", "")
        color = ROLE_COLORS.get(role, "#374151")
        label = ROLE_LABELS.get(role, role)
        desc  = ROLE_DESCRIPTIONS.get(role, "")

        # Role badge card
        st.markdown(
            f"""
            <div style="
                background: {color}12;
                border: 1px solid {color}40;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 12px 14px;
                margin-bottom: 4px;
            ">
                <div style="font-size:11px; color:{color}; font-weight:700;
                            letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px;">
                    Signed in as
                </div>
                <div style="font-size:16px; font-weight:700; margin-bottom:2px;">
                    {st.session_state.get('username', '')}
                </div>
                <div style="font-size:13px; color:{color}; font-weight:600; margin-bottom:6px;">
                    {label}
                </div>
                <div style="font-size:11px; color:gray; line-height:1.5;">
                    {desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("🔒 Responses are filtered to data your role is authorized to access.")
        st.divider()

        st.markdown("**Session**")
        session_id = st.session_state.get("session_id", "")
        st.code(session_id[:8] + "...", language=None)

        st.divider()

        if st.button("🗑️  Clear conversation", use_container_width=True):
            import uuid
            st.session_state.messages   = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

        if st.button("🚪  Sign out", use_container_width=True, type="secondary"):
            token = st.session_state.get("refresh_token")
            if token:
                try:
                    asyncio.run(APIClient.logout(token))
                except Exception:
                    pass
            clear_user()
            st.switch_page("pages/1_Login.py")
