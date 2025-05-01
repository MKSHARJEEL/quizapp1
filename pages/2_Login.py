import streamlit as st
from db import get_user

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = get_user(username, password)
    if user:
        st.session_state["user_id"] = user[0]
        st.session_state["username"] = user[1]
        st.success("Login successful! Go to Home.")
    else:
        st.error("Invalid credentials.")
