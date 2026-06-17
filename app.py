import streamlit as st
from modules.utils import init_session_state
from modules.auth import login_view, register_view

st.set_page_config(
    page_title="AI Facial Analysis",
    layout="wide",
)

init_session_state()

st.markdown("""
<style>
.main-title {
    font-size: 2.6rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 0.95rem;
}
.header-left {
    font-weight: 600;
    color: #1e293b;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AI-Based Real-Time Facial Analysis & Identity Verification</div>', unsafe_allow_html=True)

# Header row
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown(
        '<div class="header-left">Modules: Face Detection • Liveness • Emotion • Age/Gender • Skin & Makeup • Database</div>',
        unsafe_allow_html=True,
    )
with header_col2:
    if st.session_state.user:
        st.success(f"Logged in: {st.session_state.user['name']}")
        if st.button("Logout", use_container_width=True, key="header_logout"):
            st.session_state.user = None
            st.session_state.auth_view = "login"
            st.rerun()
    else:
        if st.button("Login", use_container_width=True, key="header_login"):
            st.session_state.auth_view = "login"

st.markdown("---")

# Show auth view or home description
if not st.session_state.user and st.session_state.auth_view == "login":
    login_view()
elif not st.session_state.user and st.session_state.auth_view == "register":
    register_view()
else:
    # Home content when logged in OR when no auth_view requested yet
    st.subheader("Project Overview")
    st.write("""
This system implements multiple real-time facial analysis modules:

- Real-time face detection & tracking  
- Liveness detection (blink + depth cues)  
- Micro-movement and facial expression analysis  
- Age, gender, and emotion classification  
- Skin texture and makeup analysis with removal  
- Identity-linked database using MongoDB
    """)
    st.info("Use the sidebar to open modules like **1_RealTime_Face_Analysis**.")
