import streamlit as st
import os
import json
from db_utils import init_db, insert_quiz

init_db()
st.set_page_config(page_title="AI Quiz App", page_icon="🤖")

# Load API key
api_key = st.secrets.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = api_key or ""

st.title("🤖 AI Quiz App")

if "user_id" not in st.session_state:
    st.warning("Please log in from the Login page.")
else:
    st.success(f"Logged in as: {st.session_state['username']}")

    # Example quiz question
    question = "What is 2 + 2?"
    answer = st.text_input("Question: " + question)

    if st.button("Submit Answer"):
        score = 1 if answer.strip() == "4" else 0
        quiz_data = json.dumps({"question": question, "answer": answer})
        insert_quiz(st.session_state["user_id"], quiz_data, score)
        st.success(f"Your score: {score}")
