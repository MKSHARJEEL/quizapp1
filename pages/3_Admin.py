import streamlit as st
from db_utils import get_admin, get_all_users, get_all_quizzes

st.title("Admin Dashboard")

username = st.text_input("Admin Username")
password = st.text_input("Admin Password", type="password")

if st.button("Login as Admin"):
    admin = get_admin(username, password)
    if admin:
        st.success("Admin logged in successfully!")
        st.subheader("All Users")
        st.write(get_all_users())
        st.subheader("All Quizzes")
        st.write(get_all_quizzes())
    else:
        st.error("Invalid admin credentials.")
