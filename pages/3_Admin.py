import streamlit as st
from db import get_all_users, get_all_quizzes

st.title("Admin Dashboard")

admin_user = st.text_input("Admin Username")
admin_pass = st.text_input("Admin Password", type="password")

if st.button("Login as Admin"):
    if admin_user == "admin" and admin_pass == "adminpass":  # improve this later!
        st.success("Admin logged in.")

        st.subheader("All Users")
        users = get_all_users()
        st.write(users)

        st.subheader("All Quizzes")
        quizzes = get_all_quizzes()
        st.write(quizzes)
    else:
        st.error("Invalid admin credentials.")
