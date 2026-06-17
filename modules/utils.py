# # # modules/utils.py
# # import hashlib
# # import streamlit as st

# # def hash_password(password: str) -> str:
# #     return hashlib.sha256(password.encode("utf-8")).hexdigest()

# # def verify_password(password: str, password_hash: str) -> bool:
# #     return hash_password(password) == password_hash

# # def init_session_state():
# #     if "user" not in st.session_state:
# #         st.session_state.user = None  # dict with {_id, name, email}
# import hashlib
# import streamlit as st

# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()

# def verify_password(password: str, password_hash: str) -> bool:
#     return hash_password(password) == password_hash

# def init_session_state():
#     if "user" not in st.session_state:
#         st.session_state.user = None
#     if "show_login_page" not in st.session_state:
#         st.session_state.show_login_page = False
#     if "show_register" not in st.session_state:
#         st.session_state.show_register = False
import hashlib
import streamlit as st

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_view" not in st.session_state:
        # "none", "login", "register"
        st.session_state.auth_view = "none"
