import streamlit as st

st.set_page_config(
    page_title="CGI Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Redirect to login if not authenticated
if not st.session_state.get("access_token"):
    st.switch_page("pages/2_Chat.py")
else:
    st.switch_page("pages/2_Chat.py")
