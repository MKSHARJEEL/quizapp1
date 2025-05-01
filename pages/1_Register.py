import streamlit as st
from db import insert_user

st.title("Register")

username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Register"):
    try:
        insert_user(username, password, email)
        st.success("User registered successfully! Go to Login page.")
    except Exception as e:
        st.error(f"Error: {e}")
