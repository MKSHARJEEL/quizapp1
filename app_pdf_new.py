from db_utils import insert_quiz

if "user_id" in st.session_state:
    insert_quiz(st.session_state["user_id"], json.dumps(st.session_state.questions), score)
