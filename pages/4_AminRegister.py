import streamlit as st
from db import insert_admin

st.title("Admin Registration")

username = st.text_input("Admin Username")
password = st.text_input("Admin Password", type="password")

if st.button("Register Admin"):
    try:
        insert_admin(username, password)
        st.success("Admin registered successfully! Go to the Admin Login page.")
    except Exception as e:
        st.error(f"Error: {e}")
