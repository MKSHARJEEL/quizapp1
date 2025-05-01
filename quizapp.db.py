import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Set up database connection and session
Base = declarative_base()
engine = create_engine('sqlite:///quizapp.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Define models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(50), default="user")  # Default role is 'user'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Admin(User):
    __tablename__ = 'admins'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)

class Quiz(Base):
    __tablename__ = 'quizzes'
    id = Column(Integer, primary_key=True)
    question = Column(String(500), nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(200), nullable=False)

class UserQuizMarks(Base):
    __tablename__ = 'user_quiz_marks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    marks = Column(Integer, nullable=False)

    user = relationship('User', back_populates="marks")
    quiz = relationship('Quiz', back_populates="marks")

User.marks = relationship('UserQuizMarks', back_populates="user")
Quiz.marks = relationship('UserQuizMarks', back_populates="quiz")

# Create tables
Base.metadata.create_all(engine)

# Streamlit Registration Form
def register_user(email, password, role):
    user = User(email=email, role=role)
    user.set_password(password)
    session.add(user)
    session.commit()
    st.success("Registration successful. You can now log in.")

# Streamlit Login Form
def login_user(email, password):
    user = session.query(User).filter_by(email=email).first()
    if user and user.check_password(password):
        return user
    return None

# Function for user registration
def registration_form():
    st.subheader("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Register"):
        if email and password:
            register_user(email, password, role)
        else:
            st.error("Please fill in all fields.")

# Function for user login
def login_form():
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.user = user  # Store the user in session
            st.success(f"Welcome {user.email}")
            return user
        else:
            st.error("Invalid credentials")

# Main Streamlit App
def main():
    st.title("Quiz App with User Authentication")
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        registration_form()
    else:
        user = login_form()
        if user:
            st.session_state.user = user  # Store the user in session
            # Further app logic (like displaying quiz data) goes here

if __name__ == "__main__":
    main()
