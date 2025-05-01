import streamlit as st
from db import get_admin, get_all_users, get_all_quizzes

st.title("Admin Login")

username = st.text_input("Admin Username")
password = st.text_input("Admin Password", type="password")

if st.button("Login as Admin"):
    admin = get_admin(username, password)
    if admin:
        st.success("Admin logged in successfully!")

        st.subheader("All Users")
        users = get_all_users()
        st.write(users)

        st.subheader("All Quizzes")
        quizzes = get_all_quizzes()
        st.write(quizzes)
    else:
        st.error("Invalid admin credentials.")
