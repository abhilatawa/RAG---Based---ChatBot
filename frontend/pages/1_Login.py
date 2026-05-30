import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import streamlit as st
import httpx

from utils.session_state import init_session, set_user, is_logged_in, ROLE_LABELS, ROLE_COLORS
from utils.api_client import APIClient

st.set_page_config(
    page_title="FinSolve — Sign In",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_session()

if is_logged_in():
    st.switch_page("pages/2_Chat.py")

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default Streamlit chrome on login page */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; max-width: 480px; }

    /* Card */
    .login-card {
        background: var(--background-color);
        border: 1px solid rgba(128,128,128,.2);
        border-radius: 16px;
        padding: 36px 40px 28px;
        box-shadow: 0 4px 24px rgba(0,0,0,.08);
        margin-bottom: 20px;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid rgba(128,128,128,.3) !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #185FA5 !important;
        box-shadow: 0 0 0 3px rgba(24,95,165,.12) !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        border-radius: 8px !important;
        height: 44px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #185FA5, #1d4ed8) !important;
        border: none !important;
        letter-spacing: .02em;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8, #185FA5) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(24,95,165,.3) !important;
    }

    /* Demo badge */
    .demo-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        cursor: pointer;
        margin: 3px 4px;
        transition: all .15s;
    }
    .demo-badge:hover { opacity: .8; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)


# ── Hero section ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; padding: 12px 0 28px;'>
        <div style='font-size:52px; margin-bottom:8px;'>🏦</div>
        <h1 style='font-size:26px; font-weight:800; margin:0 0 6px;
                   letter-spacing:-.02em;'>CGI   Assistant</h1>
        <p style='color:gray; font-size:14px; margin:0; line-height:1.6;'>
            Secure AI — your role, your data.<br/>
            Every response is grounded in documents your role can access.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Login form ────────────────────────────────────────────────────────────────
with st.form("login_form", clear_on_submit=False):
    username = st.text_input(
        "Username",
        placeholder="e.g. alice.finance",
        autocomplete="username",
    )
    password = st.text_input(
        "Password",
        type="password",
        placeholder="••••••••",
        autocomplete="current-password",
    )
    submitted = st.form_submit_button(
        "Sign in  →",
        use_container_width=True,
        type="primary",
    )

# ── Login logic ───────────────────────────────────────────────────────────────
if submitted:
    if not username.strip() or not password.strip():
        st.error("Please enter both username and password.")
    else:
        with st.spinner("Authenticating…"):
            try:
                data = asyncio.run(APIClient.login(username.strip(), password))
                set_user(data)
                st.success(f"Welcome back, {data['username']}! Redirecting…")
                st.switch_page("pages/2_Chat.py")

            except httpx.ConnectError:
                st.warning(
                    "⚠️  **Backend not running yet** — that's fine for now!\n\n"
                    "The login UI is working correctly. Start the FastAPI backend "
                    "(`uvicorn backend.app.main:app`) and try again.",
                    icon="🔌",
                )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    st.error("❌  Invalid username or password.")
                elif e.response.status_code == 429:
                    detail = e.response.json().get("detail", "Too many attempts.")
                    st.warning(f"⏳  {detail}")
                else:
                    st.error(f"Server error ({e.response.status_code}). Try again shortly.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ── Security trust badges ─────────────────────────────────────────────────────
st.markdown(
    """
    <div style='text-align:center; margin-top:20px; padding: 14px;
                border-top: 1px solid rgba(128,128,128,.15);'>
        <span style='font-size:12px; color:gray; margin:0 12px;'>🔒 JWT RS256</span>
        <span style='font-size:12px; color:gray; margin:0 12px;'>🛡️ RBAC</span>
        <span style='font-size:12px; color:gray; margin:0 12px;'>🔐 bcrypt</span>
        <span style='font-size:12px; color:gray; margin:0 12px;'>📋 Audit logs</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Demo credentials helper ───────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center; font-size:13px; color:gray; margin-bottom:10px;'>"
    "🧪  <strong>Demo credentials</strong> — click to autofill</p>",
    unsafe_allow_html=True,
)

DEMO_USERS = [
    ("alice.finance",  "finance"),
    ("bob.hr",         "hr"),
    ("carol.eng",      "engineering"),
    ("david.mktg",     "marketing"),
    ("eve.ceo",        "c_level"),
    ("frank.emp",      "employee"),
]

cols = st.columns(3)
for i, (uname, role) in enumerate(DEMO_USERS):
    color = ROLE_COLORS.get(role, "#374151")
    label = ROLE_LABELS.get(role, role).split(" ", 1)[-1]  # strip emoji
    with cols[i % 3]:
        if st.button(
            f"{uname}\n{label}",
            key=f"demo_{uname}",
            use_container_width=True,
            help=f"Fill username: {uname} / password: Password123!",
        ):
            st.session_state["_prefill_user"] = uname
            st.session_state["_prefill_pass"] = "Password123!"
            st.info(f"Prefilled: **{uname}** / `Password123!`  \nClick **Sign in** above.")
