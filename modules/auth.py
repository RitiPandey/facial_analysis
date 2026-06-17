# # # modules/auth.py
# # import streamlit as st
# # from modules.db import Database
# # from modules.utils import hash_password, verify_password

# # db = Database()

# # def registration_form():
# #     st.subheader("📝 Registration")
# #     name = st.text_input("Full Name")
# #     email = st.text_input("Email")
# #     password = st.text_input("Password", type="password")
# #     confirm = st.text_input("Confirm Password", type="password")

# #     if st.button("Create Account", use_container_width=True):
# #         if not name or not email or not password:
# #             st.error("All fields are required.")
# #         elif password != confirm:
# #             st.error("Passwords do not match.")
# #         else:
# #             ok = db.create_user(name, email, hash_password(password))
# #             if ok:
# #                 st.success("Account created. Please log in.")
# #             else:
# #                 st.error("User already exists or DB error.")

# # def login_form():
# #     st.subheader("🔐 Login")
# #     email = st.text_input("Email", key="login_email")
# #     password = st.text_input("Password", type="password", key="login_password")

# #     if st.button("Login", use_container_width=True):
# #         user = db.get_user_by_email(email)
# #         if user and verify_password(password, user["password_hash"]):
# #             st.session_state.user = {
# #                 "id": str(user["_id"]),
# #                 "name": user["name"],
# #                 "email": user["email"],
# #             }
# #             st.success(f"Welcome, {user['name']}!")
# #             st.rerun()
# #         else:
# #             st.error("Invalid email or password.")

# import streamlit as st
# from modules.db import Database
# from modules.utils import hash_password, verify_password

# db = Database()

# def registration_modal():
#     """Registration form shown as a 'popup' style card."""
#     st.markdown(
#         """
#         <div style="
#             position: fixed;
#             top: 0; left: 0;
#             width: 100%; height: 100%;
#             background: rgba(0,0,0,0.55);
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             z-index: 9999;
#         ">
#           <div style="
#               background: #ffffff;
#               padding: 2rem;
#               border-radius: 1rem;
#               width: 400px;
#               box-shadow: 0 15px 40px rgba(0,0,0,0.25);
#           ">
#         """,
#         unsafe_allow_html=True,
#     )

#     st.markdown("### 📝 Create an account")
#     name = st.text_input("Full Name", key="reg_name")
#     email = st.text_input("Email", key="reg_email")
#     password = st.text_input("Password", type="password", key="reg_password")
#     confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Sign Up", use_container_width=True):
#             if not name or not email or not password:
#                 st.error("All fields are required.")
#             elif password != confirm:
#                 st.error("Passwords do not match.")
#             else:
#                 ok = db.create_user(name, email, hash_password(password))
#                 if ok:
#                     st.success("Account created. Please login.")
#                     st.session_state.show_register = False
#                 else:
#                     st.error("User already exists or DB error.")
#     with col2:
#         if st.button("Cancel", use_container_width=True):
#             st.session_state.show_register = False

#     st.markdown("</div></div>", unsafe_allow_html=True)


# def login_page():
#     """Full-page login card with a 'Register' link underneath."""
#     st.markdown(
#         """
#         <style>
#         .login-card {
#             max-width: 420px;
#             margin: 2rem auto;
#             padding: 2rem 2.5rem;
#             border-radius: 1.2rem;
#             background: linear-gradient(135deg, #f8fafc, #e5edff);
#             box-shadow: 0 18px 45px rgba(15,23,42,0.22);
#         }
#         .login-title {
#             text-align: center;
#             font-size: 1.6rem;
#             font-weight: 800;
#             color: #1e293b;
#         }
#         </style>
#         <div class="login-card">
#         <div class="login-title">🔐 Login to Continue</div>
#         <p style="text-align:center; color:#475569; margin-top:0.3rem;">
#             Access real-time facial analysis modules after login.
#         </p>
#         """,
#         unsafe_allow_html=True,
#     )

#     email = st.text_input("Email", key="login_email_new")
#     password = st.text_input("Password", type="password", key="login_password_new")

#     if st.button("Login", use_container_width=True):
#         user = db.get_user_by_email(email)
#         if user and verify_password(password, user["password_hash"]):
#             st.session_state.user = {
#                 "id": str(user["_id"]),
#                 "name": user["name"],
#                 "email": user["email"],
#             }
#             st.success(f"Welcome, {user['name']}!")
#             st.session_state.show_login_page = False
#             st.rerun()
#         else:
#             st.error("Invalid email or password.")

#     st.markdown(
#         """
#         <hr style="margin: 1.2rem 0; border: none; border-top: 1px solid #cbd5f5;">
#         <p style="text-align:center; color:#64748b;">
#             Don't have an account?
#         </p>
#         """,
#         unsafe_allow_html=True,
#     )

#     # Register link
#     if st.button("Create new account", use_container_width=True):
#         st.session_state.show_register = True

#     st.markdown("</div>", unsafe_allow_html=True)  # close card

import streamlit as st
from modules.db import Database
from modules.utils import hash_password, verify_password

db = Database()

def login_view():
    st.markdown(
        """
        <style>
        .auth-card {
            max-width: 420px;
            margin: 2.5rem auto;
            padding: 2rem 2.4rem;
            border-radius: 1.2rem;
            background: linear-gradient(135deg, #f8fafc, #e5edff);
            box-shadow: 0 18px 40px rgba(15,23,42,0.25);
        }
        .auth-title {
            text-align: center;
            font-size: 1.6rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.4rem;
        }
        .auth-subtitle {
            text-align: center;
            color: #64748b;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        </style>
        <div class="auth-card">
          <div class="auth-title">Welcome back</div>
          <div class="auth-subtitle">Log in to access facial analysis modules</div>
        """,
        unsafe_allow_html=True,
    )

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", use_container_width=True, key="login_button_main"):
        user = db.get_user_by_email(email)
        if user and verify_password(password, user["password_hash"]):
            st.session_state.user = {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
            }
            st.success(f"Welcome, {user['name']}!")
            st.session_state.auth_view = "none"
            st.rerun()
        else:
            st.error("Invalid email or password.")

    st.markdown(
        """
        <hr style="margin: 1.4rem 0; border: none; border-top: 1px solid #cbd5f5;">
        <p style="text-align:center; color:#64748b;">
          Don't have an account?
          <a style="color:#2563eb; text-decoration:none;" href="#" onclick="false;">
            </a>
        </p>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Create new account", use_container_width=True, key="go_register_button"):
        st.session_state.auth_view = "register"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def register_view():
    st.markdown(
        """
        <div class="auth-card">
          <div class="auth-title">Create an account</div>
          <div class="auth-subtitle">Register to save your analysis history</div>
        """,
        unsafe_allow_html=True,
    )

    name = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign Up", use_container_width=True, key="register_button_main"):
            if not name or not email or not password:
                st.error("All fields are required.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                ok = db.create_user(name, email, hash_password(password))
                if ok:
                    st.success("Account created. You can log in now.")
                    st.session_state.auth_view = "login"
                    st.rerun()
                else:
                    st.error("User already exists or database error.")
    with col2:
        if st.button("Back to Login", use_container_width=True, key="back_to_login_button"):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
