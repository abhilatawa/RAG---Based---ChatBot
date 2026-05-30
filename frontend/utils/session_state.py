import streamlit as st
import uuid

ROLE_COLORS = {
    "finance":     "#185FA5",
    "hr":          "#0F6E56",
    "engineering": "#B45309",
    "marketing":   "#9D2235",
    "c_level":     "#5B21B6",
    "employee":    "#374151",
}

ROLE_LABELS = {
    "finance":     "💼 Finance",
    "hr":          "👥 Human Resources",
    "engineering": "⚙️ Engineering",
    "marketing":   "📣 Marketing",
    "c_level":     "🏛️ C-Level Executive",
    "employee":    "🧑‍💼 Employee",
}

ROLE_DESCRIPTIONS = {
    "finance":     "Access to financial reports, budgets & forecasts",
    "hr":          "Access to HR policies, headcount & compensation data",
    "engineering": "Access to technical docs, system architecture & roadmaps",
    "marketing":   "Access to campaign data, market research & brand assets",
    "c_level":     "Full access across all departments",
    "employee":    "Access to company-wide announcements & general policies",
}


def init_session():
    defaults = {
        "access_token":  None,
        "refresh_token": None,
        "username":      None,
        "role":          None,
        "session_id":    str(uuid.uuid4()),
        "messages":      [],
        "is_loading":    False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def is_logged_in() -> bool:
    return bool(st.session_state.get("access_token"))


def set_user(token_data: dict):
    st.session_state.access_token  = token_data["access_token"]
    st.session_state.refresh_token = token_data.get("refresh_token", "")
    st.session_state.username       = token_data["username"]
    st.session_state.role           = token_data["role"]
    st.session_state.session_id     = str(uuid.uuid4())
    st.session_state.messages       = []


def clear_user():
    for key in ["access_token", "refresh_token", "username", "role", "messages"]:
        st.session_state[key] = None
    st.session_state.session_id = str(uuid.uuid4())
