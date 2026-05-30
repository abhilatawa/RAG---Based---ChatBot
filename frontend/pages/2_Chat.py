import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import httpx
import streamlit as st
from utils.session_state import init_session, is_logged_in, ROLE_COLORS, ROLE_LABELS
from components.sidebar import render_sidebar
from components.source_card import render_sources

st.set_page_config(
    page_title="CGI Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

if not is_logged_in():
    st.switch_page("pages/1_Login.py")

# ── Role context ──────────────────────────────────────────────────────────────
BASE_URL = "http://localhost:8000/api/v1"
ROLE     = st.session_state.get("role", "employee")
COLOR    = ROLE_COLORS.get(ROLE, "#374151")
LABEL    = ROLE_LABELS.get(ROLE, ROLE)
INITIALS = (st.session_state.get("username", "U") or "U")[0].upper()

# ── Page styles ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.2rem; padding-bottom: 0; }}

    /* ── Avatars ── */
    .av {{
        width: 36px; height: 36px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; font-weight: 700; flex-shrink: 0;
    }}
    .av-user {{ background:{COLOR}22; border:2px solid {COLOR}55; color:{COLOR}; }}
    .av-bot  {{ background:#1e293b; border:2px solid #334155; color:#94a3b8; }}

    /* ── Message rows ── */
    .msg-row {{
        display: flex; gap: 12px; margin-bottom: 18px; align-items: flex-start;
    }}
    .msg-row.right {{ flex-direction: row-reverse; }}

    /* ── Bubbles ── */
    .bubble {{
        max-width: 70%; padding: 11px 15px; font-size: 14px;
        line-height: 1.7; border-radius: 16px;
    }}
    .bubble-user {{
        background: {COLOR}16; border: 1px solid {COLOR}30;
        border-top-right-radius: 4px;
    }}
    .bubble-bot {{
        background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.1);
        border-top-left-radius: 4px;
    }}

    /* ── Typing dots ── */
    .typing {{ display:flex; gap:5px; align-items:center; padding:4px 2px; }}
    .dot {{
        width:8px; height:8px; border-radius:50%; background:#64748b;
        animation: blink 1.2s infinite;
    }}
    .dot:nth-child(2) {{ animation-delay:.2s; }}
    .dot:nth-child(3) {{ animation-delay:.4s; }}
    @keyframes blink {{
        0%,80%,100% {{ transform:translateY(0); opacity:.4; }}
        40%          {{ transform:translateY(-5px); opacity:1; }}
    }}

    /* ── Empty state ── */
    .empty {{
        text-align:center; padding:48px 20px 32px; color:gray;
    }}
    .empty .icon {{ font-size:48px; margin-bottom:10px; }}
    .empty h3 {{ font-size:20px; font-weight:700; margin:0 0 8px; color:inherit; }}
    .empty p  {{ font-size:14px; line-height:1.65; max-width:420px; margin:0 auto; }}

    /* ── Suggestion chips ── */
    div[data-testid="stButton"] button {{
        border-radius: 20px !important;
        font-size: 12px !important;
        padding: 4px 12px !important;
        border: 1px solid rgba(255,255,255,.12) !important;
        background: rgba(255,255,255,.04) !important;
        transition: all .15s !important;
    }}
    div[data-testid="stButton"] button:hover {{
        border-color: {COLOR}55 !important;
        background: {COLOR}14 !important;
        color: {COLOR} !important;
    }}

    /* ── Header badge ── */
    .role-badge {{
        display:inline-block;
        background:{COLOR}18; border:1px solid {COLOR}44;
        border-radius:20px; padding:3px 12px;
        font-size:13px; font-weight:600; color:{COLOR};
    }}

    /* ── Chat input ── */
    .stChatInput textarea {{
        border-radius: 12px !important;
        font-size: 14px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
render_sidebar()

# ── Page header ───────────────────────────────────────────────────────────────
c1, c2 = st.columns([4, 1])
with c1:
    st.markdown("## 💬 FinSolve Assistant")
with c2:
    st.markdown(
        f"<div style='text-align:right;padding-top:10px;'>"
        f"<span class='role-badge'>{LABEL}</span></div>",
        unsafe_allow_html=True,
    )

st.divider()

# ── Role-aware suggestion chips ───────────────────────────────────────────────
SUGGESTIONS = {
    "finance":     [
        "What was our Q3 revenue?",
        "Show me operating margin trends",
        "What's our current burn rate?",
        "Summarise the latest budget forecast",
    ],
    "hr":          [
        "What is the leave policy?",
        "How many open positions do we have?",
        "Show me the onboarding checklist",
        "What are the performance review dates?",
    ],
    "engineering": [
        "What's in the current sprint?",
        "Explain our system architecture",
        "What are the API rate limits?",
        "Show me the incident runbook",
    ],
    "marketing":   [
        "What was the Q3 campaign ROI?",
        "Show me brand guidelines",
        "What's the content calendar?",
        "Summarise the latest market research",
    ],
    "c_level":     [
        "Give me a cross-department summary",
        "What are the key risks this quarter?",
        "Show headcount vs budget",
        "What's our runway at current burn?",
    ],
    "employee":    [
        "What are the company holidays?",
        "How do I submit an expense?",
        "Where is the employee handbook?",
        "What's the remote work policy?",
    ],
}

# ── Helper: render bubbles ────────────────────────────────────────────────────
def user_bubble(text: str):
    st.markdown(
        f"""<div class="msg-row right">
              <div class="av av-user">{INITIALS}</div>
              <div class="bubble bubble-user">{text}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def bot_bubble(text: str, sources: list = None):
    st.markdown(
        f"""<div class="msg-row">
              <div class="av av-bot">🏦</div>
              <div class="bubble bubble-bot">{text}</div>
            </div>""",
        unsafe_allow_html=True,
    )
    if sources:
        st.markdown("<div style='margin-left:48px;'>", unsafe_allow_html=True)
        render_sources(sources)
        st.markdown("</div>", unsafe_allow_html=True)


def typing_bubble():
    st.markdown(
        """<div class="msg-row">
             <div class="av av-bot">🏦</div>
             <div class="bubble bubble-bot">
               <div class="typing">
                 <div class="dot"></div>
                 <div class="dot"></div>
                 <div class="dot"></div>
               </div>
             </div>
           </div>""",
        unsafe_allow_html=True,
    )


# ── API call ──────────────────────────────────────────────────────────────────
async def call_chat(query: str) -> dict:
    headers = {"Authorization": f"Bearer {st.session_state.get('access_token', '')}"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BASE_URL}/chat/query",
            json={
                "query":      query,
                "session_id": st.session_state.get("session_id"),
                "top_k":      5,
            },
            headers=headers,
        )
        r.raise_for_status()
        return r.json()


# ── Render conversation history ───────────────────────────────────────────────
messages = st.session_state.get("messages", [])

if not messages:
    # Empty state
    suggestions = SUGGESTIONS.get(ROLE, [])
    st.markdown(
        f"""<div class="empty">
              <div class="icon">🏦</div>
              <h3>How can I help you today?</h3>
              <p>Ask me anything your <strong>{LABEL}</strong> role has access to.
                 Every answer is grounded in authorized company documents only.</p>
            </div>""",
        unsafe_allow_html=True,
    )

    # Suggestion chips
    if suggestions:
        st.markdown(
            "<p style='text-align:center;font-size:12px;color:gray;"
            "margin:4px 0 10px;'>Try asking…</p>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            with cols[i]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state["_pending"] = s
                    st.rerun()
else:
    for msg in messages:
        if msg["role"] == "user":
            user_bubble(msg["content"])
        else:
            bot_bubble(msg["content"], msg.get("sources", []))


# ── Chat input ────────────────────────────────────────────────────────────────
pending = st.session_state.pop("_pending", None)
typed   = st.chat_input(
    f"Message FinSolve Assistant…",
    disabled=st.session_state.get("is_loading", False),
)
active_query = typed or pending

if active_query:
    st.session_state.is_loading = True
    st.session_state.messages.append({
        "role": "user", "content": active_query, "sources": []
    })

    # Render user bubble + typing indicator immediately
    user_bubble(active_query)
    slot = st.empty()
    with slot:
        typing_bubble()

    # Hit the backend
    try:
        data    = asyncio.run(call_chat(active_query))
        answer  = data.get("answer", "No response received.")
        sources = data.get("sources", [])

    except httpx.ConnectError:
        answer  = "⚠️ Cannot reach the backend. Make sure FastAPI is running on port 8000."
        sources = []
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            answer = "⚠️ Your session has expired. Please sign out and sign in again."
            st.session_state.access_token = None
        else:
            answer = f"⚠️ Server error {e.response.status_code}. Please try again."
        sources = []
    except Exception as e:
        answer  = f"⚠️ Unexpected error: {e}"
        sources = []

    slot.empty()
    bot_bubble(answer, sources)

    st.session_state.messages.append({
        "role": "assistant", "content": answer, "sources": sources
    })
    st.session_state.is_loading = False
    st.rerun()
