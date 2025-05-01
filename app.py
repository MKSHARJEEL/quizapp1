import streamlit as st
import os
import json
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from google.generativeai import GenerativeModel
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain.vectorstores import FAISS

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Configure Generative AI model
def get_gemini_response(prompt):
    model = GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    response = model.generate_content(prompt)
    return response.text

def get_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    raw_text = ""
    for page in pdf_reader.pages:
        raw_text += page.extract_text()
    return raw_text

def get_quiz_parameters():
    st.sidebar.title('Quiz Parameters')
    num_questions = st.sidebar.slider('Number of questions: ', min_value=1, max_value=10, value=1)
    quiz_type = st.sidebar.selectbox('Type of Quiz: ', ('Select.....', 'Multiple-Choice', 'True-False'))
    quiz_level = st.sidebar.selectbox('Quiz Level: ', ('Select.....', 'Easy', 'Medium', 'Hard'))
    language = st.sidebar.selectbox('Quiz Language: ', ('Select.....', 'English', 'Urdu', 'French'))
    return num_questions, quiz_type, quiz_level, language

def get_sub_options(main_option):
    sub_options = {
        'Machine Learning': ['Select.....', 'Supervised Learning', 'Unsupervised Learning', 'Semi-Supervised Learning', 'Reinforcement Learning'],
        'Deep Learning': ['Select.....', 'Artificial Neural Networks (ANNs)', 'Convolutional Neural Networks (CNNs)', 'Recurrent Neural Networks (RNNs)'],
        'Mathematics': ['Select.....', 'Linear Algebra', 'Calculus', 'Matrices', 'Vectors'],
        'Statistics': ['Select.....', 'Descriptive', 'Probability', 'Inferential']
    }
    return sub_options.get(main_option, ['Select.....'])

def handle_quiz_generation(prompt):
    response = get_gemini_response(prompt)
    try:
        all_questions = json.loads(response)
        unique_questions = [q for q in all_questions if q not in st.session_state.history]
        
        if len(unique_questions) < len(st.session_state.user_answers):
            st.warning(f"Only {len(unique_questions)} unique questions were generated.")
        st.session_state.questions = unique_questions
        st.session_state.history.extend(unique_questions)
        st.session_state.user_answers = {f"q{i+1}": None for i in range(len(st.session_state.questions))}
    except json.JSONDecodeError:
        st.error("Failed to parse the quiz questions. Please try again.")

def display_quiz_questions():
    if st.session_state.questions:
        st.subheader("Quiz Questions")
        for i, q in enumerate(st.session_state.questions):
            st.write(f"**Q{i+1}: {q['question']}**")
            if 'options' in q:
                selected_option = st.radio(f"Select an answer for Q{i+1}:", options=q['options'], key=f"q{i+1}")
            else:
                selected_option = st.radio(f"Select True or False for Q{i+1}:", options=['True', 'False'], key=f"q{i+1}")
            st.session_state.user_answers[f"q{i+1}"] = selected_option
            st.write("---")

        if st.button('Submit Answers'):
            st.subheader("Quiz Results")
            score = 0
            for i, q in enumerate(st.session_state.questions):
                correct_answer = q['answer']
                user_answer = st.session_state.user_answers[f"q{i+1}"]
                if user_answer == correct_answer:
                    score += 1
                    st.write(f"**Q{i+1}: {q['question']}** - Correct!")
                else:
                    st.write(f"**Q{i+1}: {q['question']}** - Incorrect.")
                    st.write(f"Correct answer: **{correct_answer}**")
                st.write(f"Explanation: {q['explanation']}")
                st.write("---")
            st.success(f"Your score is {score}/{len(st.session_state.questions)}!")

def main():
    st.set_page_config(page_title="Quiz App", page_icon='🤖', layout='centered', initial_sidebar_state='collapsed')
    st.title('AI Quiz Generator')

    # Initialize session state
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'history' not in st.session_state:
        st.session_state.history = []

    # Sidebar for initial choice
    st.sidebar.title('Please select an option')
    initial_choice = st.sidebar.selectbox(
        'Please choose how you would like to proceed:',
        ('Select.....', 'Upload PDF/Text File', 'Data Science', 'Enter the Topic')
    )

    if initial_choice == 'Upload PDF/Text File':
        uploaded_file = st.sidebar.file_uploader("Upload a PDF to create a quiz from its content.", type=["pdf"])

        if uploaded_file:
            pdf_text = get_pdf_text(uploaded_file)
            num_questions, quiz_type, quiz_level, language = get_quiz_parameters()

            if st.sidebar.button('Generate Quiz'):
                if quiz_type != 'Select.....' and quiz_level != 'Select.....' and language != 'Select.....':
                    prompt = f"""
                    Using the following JSON schema, generate unique quiz questions based on the selected parameters:
                    - **Number of Questions**: {num_questions}
                    - **Type of Quiz**: {quiz_type}
                    - **Difficulty Level**: {quiz_level}
                    - **Language**: {language} 
                    Ensure that none of the questions have been previously asked (refer to the provided history of questions).
                    The questions should be well-structured and cover a range of topics within the following content:
                    
                    {pdf_text}

                    Depending on the selected quiz type, structure the questions as follows:

                    1. **For Multiple Choice:**
                    - Each question should have four possible answer options.
                    - Include one correct answer.
                    - Provide an explanation for the correct answer.

                    2. **For True/False:**
                    - Each question should be a true/false statement.
                    - Indicate the correct answer (either "True" or "False").
                    - Provide an explanation for the correct answer.

                    Please provide the questions in the following JSON format:

                    **For Multiple Choice:**
                    [
                        {{
                            "question": "string",         # The quiz question text
                            "options": [                  # A list of four possible answer options
                                "option1",
                                "option2",
                                "option3",
                                "option4"
                            ],
                            "answer": "string",           # The correct answer option
                            "explanation": "string"       # A brief explanation for why the answer is correct
                        }},
                        ...
                    ]

                    **For True/False:**
                    [
                        {{
                            "question": "string",         # The true/false statement
                            "answer": "True/False",       # The correct answer (True or False)
                            "explanation": "string"       # A brief explanation for why the answer is correct
                        }},
                        ...
                    ]

                    Notes:
                    Ensure that all questions are unique and have not been asked before (refer to the history provided).
                    The explanations should be clear and concise, providing context or additional information about the correct answer.
                    Review and format the JSON response to ensure it matches the provided schema.
                    """
                    handle_quiz_generation(prompt)
                else:
                    st.error("Please select quiz parameters including type, level and language.")

    elif initial_choice == 'Data Science':
        main_option = st.sidebar.selectbox('Choose a main Subject:', ('Select.....', 'Machine Learning', 'Deep Learning', 'Mathematics', 'Statistics'))
        sub_option = st.sidebar.selectbox('Select a sub-field:', get_sub_options(main_option)) if main_option != 'Select.....' else 'Select.....'
        num_questions, quiz_type, quiz_level, language = get_quiz_parameters()

        if st.sidebar.button('Generate Quiz'):
            if main_option != 'Select.....' and sub_option != 'Select.....' and quiz_type != 'Select.....' and quiz_level != 'Select.....' and language != 'Select.....':
                prompt = f"""
                Using the following JSON schema, generate unique quiz questions based on the selected parameters:
                - **Subject**: {main_option}
                - **Sub-field**: {sub_option}
                - **Number of Questions**: {num_questions}
                - **Type of Quiz**: {quiz_type}
                - **Difficulty Level**: {quiz_level}
                - **Language**: {language} 
                Ensure that none of the questions have been previously asked (refer to the provided history of questions).
                The questions should be well-structured and cover a range of topics within {sub_option}.
                Depending on the selected quiz type, structure the questions as follows:

                1. **For Multiple Choice:**
                - Each question should have four possible answer options.
                - Include one correct answer.
                - Provide an explanation for the correct answer.

                2. **For True/False:**
                - Each question should be a true/false statement.
                - Indicate the correct answer (either "True" or "False").
                - Provide an explanation for the correct answer.

                Please provide the questions in the following JSON format:

                **For Multiple Choice:**
                [
                    {{
                        "question": "string",         # The quiz question text
                        "options": [                  # A list of four possible answer options
                            "option1",
                            "option2",
                            "option3",
                            "option4"
                        ],
                        "answer": "string",           # The correct answer option
                        "explanation": "string"       # A brief explanation for why the answer is correct
                    }},
                    ...
                ]

                **For True/False:**
                [
                    {{
                        "question": "string",         # The true/false statement
                        "answer": "True/False",       # The correct answer (True or False)
                        "explanation": "string"       # A brief explanation for why the answer is correct
                    }},
                    ...
                ]

                Notes:
                Ensure that all questions are unique and have not been asked before (refer to the history provided).
                The explanations should be clear and concise, providing context or additional information about the correct answer.
                Review and format the JSON response to ensure it matches the provided schema.
                """
                handle_quiz_generation(prompt)
            else:
                st.error("Please select a valid subject, sub-field and quiz parameters including type, level and language.")

    elif initial_choice == 'Enter the Topic':
        topic = st.sidebar.text_input("Enter the topic:")
        num_questions, quiz_type, quiz_level, language = get_quiz_parameters()

        if st.sidebar.button('Generate Quiz'):
            if topic.strip() and quiz_type != 'Select.....' and quiz_level != 'Select.....' and language != 'Select.....':
                prompt = f"""
                Using the following JSON schema, generate unique quiz questions based on the selected parameters:
                - **Number of Questions**: {num_questions}
                - **Type of Quiz**: {quiz_type}
                - **Difficulty Level**: {quiz_level}
                - **Language**: {language} 
                Ensure that none of the questions have been previously asked (refer to the provided history of questions).
                The questions should be well-structured and cover a range of topics within {topic}.
                Depending on the selected quiz type, structure the questions as follows:

                1. **For Multiple Choice:**
                - Each question should have four possible answer options.
                - Include one correct answer.
                - Provide an explanation for the correct answer.

                2. **For True/False:**
                - Each question should be a true/false statement.
                - Indicate the correct answer (either "True" or "False").
                - Provide an explanation for the correct answer.

                Please provide the questions in the following JSON format:

                **For Multiple Choice:**
                [
                    {{
                        "question": "string",         # The quiz question text
                        "options": [                  # A list of four possible answer options
                            "option1",
                            "option2",
                            "option3",
                            "option4"
                        ],
                        "answer": "string",           # The correct answer option
                        "explanation": "string"       # A brief explanation for why the answer is correct
                    }},
                    ...
                ]

                **For True/False:**
                [
                    {{
                        "question": "string",         # The true/false statement
                        "answer": "True/False",       # The correct answer (True or False)
                        "explanation": "string"       # A brief explanation for why the answer is correct
                    }},
                    ...
                ]

                Notes:
                Ensure that all questions are unique and have not been asked before (refer to the history provided).
                The explanations should be clear and concise, providing context or additional information about the correct answer.
                Review and format the JSON response to ensure it matches the provided schema.
                """
                handle_quiz_generation(prompt)
            else:
                st.error("Please enter a topic and select quiz parameters.")

    display_quiz_questions()

if __name__ == '__main__':
    main()

# def main():
#     st.set_page_config(page_title="Quiz App", page_icon='🤖', layout='centered', initial_sidebar_state='collapsed')
#     st.title('AI Quiz Generator')

#     # Initialize session state
#     if 'questions' not in st.session_state:
#         st.session_state.questions = []
#     if 'user_answers' not in st.session_state:
#         st.session_state.user_answers = {}
#     if 'history' not in st.session_state:
#         st.session_state.history = []

#     # Sidebar for initial choice
#     st.sidebar.title('Please select an option')
#     initial_choice = st.sidebar.selectbox(
#         'Please choose how you would like to proceed:',
#         ('Select.....', 'Upload PDF File', 'Data Science', 'Enter the Topic')
#     )

#     main_option = ""
#     sub_option = ""

#     if initial_choice == 'Upload PDF File':
#         st.sidebar.title("Quiz For")
#         uploaded_file = st.sidebar.file_uploader("Upload a PDF to create a quiz from its content.", type=["pdf"])

#         if uploaded_file:
#             st.sidebar.write("File uploaded. You can create a quiz based on this file's content.")

#             # Extract text from the PDF
#             pdf_text = get_pdf_text(uploaded_file)

#             st.sidebar.title('Quiz Parameters')
#             num_questions = st.sidebar.slider('Number of questions: ', min_value=1, max_value=10, value=1)
#             quiz_type = st.sidebar.selectbox('Type of Quiz: ', ('Select.....', 'Multiple-Choice', 'True-False'))
#             quiz_level = st.sidebar.selectbox('Quiz Level: ', ('Select.....', 'Easy', 'Medium', 'Hard'))
#             language = st.sidebar.selectbox('Quiz Language: ', ('Select.....', 'English', 'Urdu', 'French'))

            
#             prompt = f"""
#             Using the following JSON schema, generate unique quiz questions based on the selected parameters:
#             - **Number of Questions**: {num_questions}
#             - **Type of Quiz**: {quiz_type}
#             - **Difficulty Level**: {quiz_level}
#             - **Language**: {language} 
#             Ensure that none of the questions have been previously asked (refer to the provided history of questions).
#             The questions should be well-structured and cover a range of topics within the following content:
            
#             {pdf_text}

#             Depending on the selected quiz type, structure the questions as follows:

#             1. **For Multiple Choice:**
#             - Each question should have four possible answer options.
#             - Include one correct answer.
#             - Provide an explanation for the correct answer.

#             2. **For True/False:**
#             - Each question should be a true/false statement.
#             - Indicate the correct answer (either "True" or "False").
#             - Provide an explanation for the correct answer.

#             Please provide the questions in the following JSON format:

#             **For Multiple Choice:**
#             [
#                 {{
#                     "question": "string",         # The quiz question text
#                     "options": [                  # A list of four possible answer options
#                         "option1",
#                         "option2",
#                         "option3",
#                         "option4"
#                     ],
#                     "answer": "string",           # The correct answer option
#                     "explanation": "string"       # A brief explanation for why the answer is correct
#                 }},
#                 ...
#             ]

#             **For True/False:**
#             [
#                 {{
#                     "question": "string",         # The true/false statement
#                     "answer": "True/False",       # The correct answer (True or False)
#                     "explanation": "string"       # A brief explanation for why the answer is correct
#                 }},
#                 ...
#             ]

#             Notes:
#             Ensure that all questions are unique and have not been asked before (refer to the history provided).
#             The explanations should be clear and concise, providing context or additional information about the correct answer.
#             Review and format the JSON response to ensure it matches the provided schema.
#             """

#             button = st.sidebar.button('Generate Quiz')

#             if button:
#                 if quiz_type == 'Select.....' or quiz_level == 'Select.....' or language == 'Select.....':
#                     st.error("Please select quiz parameters including type, level and language.")
#                 else:                          
#                     response = get_gemini_response(prompt)
#                     try:
#                         all_questions = json.loads(response)
#                         unique_questions = [q for q in all_questions if q not in st.session_state.history]
                        
#                         if len(unique_questions) < num_questions:
#                             st.warning(f"Only {len(unique_questions)} unique questions were generated, but {num_questions} were requested. You may want to reduce the number of questions or try different parameters.")
#                         st.session_state.questions = unique_questions[:num_questions]
#                         st.session_state.history.extend(st.session_state.questions)
#                         st.session_state.user_answers = {f"q{i+1}": None for i in range(len(st.session_state.questions))}
#                     except json.JSONDecodeError:
#                         st.error("Failed to parse the quiz questions. Please try again.")



#     elif initial_choice == 'Data Science':
#         st.sidebar.title("Quiz For")
#         main_option = st.sidebar.selectbox('Choose a main Subject:', ('Select.....', 'Machine Learning', 'Deep Learning', 'Mathematics', 'Statistics'))

#         # Conditional sub-options based on the main option selected
#         sub_options = {
#             'Machine Learning': ['Select.....', 'Supervised Learning', 'Unsupervised Learning', 'Semi-Supervised Learning', 'Reinforcement Learning'],
#             'Deep Learning': ['Select.....', 'Artificial Neural Networks (ANNs)', 'Convolutional Neural Networks (CNNs)', 'Recurrent Neural Networks (RNNs)'],
#             'Mathematics': ['Select.....', 'Linear Algebra', 'Calculus', 'Matrices', 'Vectors'],
#             'Statistics': ['Select.....', 'Descriptive', 'Probability', 'Inferential']
#         }

#         if main_option != 'Select.....':
#             sub_option = st.sidebar.selectbox('Select a sub-field:', sub_options[main_option])
#         else:
#             sub_option = 'Select.....'

#     # Additional quiz parameters
#         st.sidebar.title('Quiz Parameters')
#         num_questions = st.sidebar.slider('Number of questions: ', min_value=1, max_value=10, value=1)
#         quiz_type = st.sidebar.selectbox('Type of Quiz: ', ('Select.....', 'Multiple-Choice', 'True-False'))
#         quiz_level = st.sidebar.selectbox('Quiz Level: ', ('Select.....', 'Easy', 'Medium', 'Hard'))
#         language = st.sidebar.selectbox('Quiz Language: ', ('Select.....', 'English', 'Urdu', 'French'))

#         # Prepare prompt to request more questions than needed
#         prompt = f"""
#         Using the following JSON schema, generate unique quiz questions based on the selected parameters:
#         - **Subject**: {main_option}
#         - **Sub-field**: {sub_option}
#         - **Number of Questions**: {num_questions}
#         - **Type of Quiz**: {quiz_type}
#         - **Difficulty Level**: {quiz_level}
#         - **Language**: {language} 
#         Ensure that none of the questions have been previously asked (refer to the provided history of questions).
#         The questions should be well-structured and cover a range of topics within {sub_option}.
#         Depending on the selected quiz type, structure the questions as follows:

#         1. **For Multiple Choice:**
#         - Each question should have four possible answer options.
#         - Include one correct answer.
#         - Provide an explanation for the correct answer.

#         2. **For True/False:**
#         - Each question should be a true/false statement.
#         - Indicate the correct answer (either "True" or "False").
#         - Provide an explanation for the correct answer.

#         Please provide the questions in the following JSON format:

#         **For Multiple Choice:**
#         [
#             {{
#                 "question": "string",         # The quiz question text
#                 "options": [                  # A list of four possible answer options
#                     "option1",
#                     "option2",
#                     "option3",
#                     "option4"
#                 ],
#                 "answer": "string",           # The correct answer option
#                 "explanation": "string"       # A brief explanation for why the answer is correct
#             }},
#             ...
#         ]

#         **For True/False:**
#         [
#             {{
#                 "question": "string",         # The true/false statement
#                 "answer": "True/False",       # The correct answer (True or False)
#                 "explanation": "string"       # A brief explanation for why the answer is correct
#             }},
#             ...
#         ]

#         Notes:
#         Ensure that all questions are unique and have not been asked before (refer to the history provided).
#         The explanations should be clear and concise, providing context or additional information about the correct answer.
#         Review and format the JSON response to ensure it matches the provided schema.
#         """

#         button = st.sidebar.button('Generate Quiz')

#         if button:
#             if initial_choice == 'Data Science':
#                 if main_option == 'Select.....' or sub_option == 'Select.....':
#                     st.error("Please select a valid subject and sub-field.")
#                 elif quiz_type == 'Select.....' or quiz_level == 'Select.....' or language == 'Select.....':
#                     st.error("Please select quiz parameters including type, level and language.")
#                 else:                          
#                     response = get_gemini_response(prompt)
#                     try:
#                         all_questions = json.loads(response)
#                         unique_questions = [q for q in all_questions if q not in st.session_state.history]
                        
#                         if len(unique_questions) < num_questions:
#                             st.warning(f"Only {len(unique_questions)} unique questions were generated, but {num_questions} were requested. You may want to reduce the number of questions or try different parameters.")
#                         st.session_state.questions = unique_questions[:num_questions]
#                         st.session_state.history.extend(st.session_state.questions)
#                         st.session_state.user_answers = {f"q{i+1}": None for i in range(len(st.session_state.questions))}
#                     except json.JSONDecodeError:
#                         st.error("Failed to parse the quiz questions. Please try again.")
    

#     elif initial_choice == 'Enter the Topic':
#         st.sidebar.title("Quiz For")
#         topic = st.sidebar.text_input("Enter the topic:")
        
#         st.sidebar.title('Quiz Parameters')
#         num_questions = st.sidebar.slider('Number of questions: ', min_value=1, max_value=10, value=1)
#         quiz_type = st.sidebar.selectbox('Type of Quiz: ', ('Select.....', 'Multiple-Choice', 'True-False'))
#         quiz_level = st.sidebar.selectbox('Quiz Level: ', ('Select.....', 'Easy', 'Medium', 'Hard'))
#         language = st.sidebar.selectbox('Quiz Language: ', ('Select.....', 'English', 'Urdu', 'French'))

#         prompt = f"""
#         Using the following JSON schema, generate unique quiz questions based on the selected parameters:
#         - **Subject**: {main_option}
#         - **Sub-field**: {sub_option}
#         - **Number of Questions**: {num_questions}
#         - **Type of Quiz**: {quiz_type}
#         - **Difficulty Level**: {quiz_level}
#         - **Language**: {language} 
#         Ensure that none of the questions have been previously asked (refer to the provided history of questions).
#         The questions should be well-structured and cover a range of topics within {topic}.
#         Depending on the selected quiz type, structure the questions as follows:

#         1. **For Multiple Choice:**
#         - Each question should have four possible answer options.
#         - Include one correct answer.
#         - Provide an explanation for the correct answer.

#         2. **For True/False:**
#         - Each question should be a true/false statement.
#         - Indicate the correct answer (either "True" or "False").
#         - Provide an explanation for the correct answer.

#         Please provide the questions in the following JSON format:

#         **For Multiple Choice:**
#         [
#             {{
#                 "question": "string",         # The quiz question text
#                 "options": [                  # A list of four possible answer options
#                     "option1",
#                     "option2",
#                     "option3",
#                     "option4"
#                 ],
#                 "answer": "string",           # The correct answer option
#                 "explanation": "string"       # A brief explanation for why the answer is correct
#             }},
#             ...
#         ]

#         **For True/False:**
#         [
#             {{
#                 "question": "string",         # The true/false statement
#                 "answer": "True/False",       # The correct answer (True or False)
#                 "explanation": "string"       # A brief explanation for why the answer is correct
#             }},
#             ...
#         ]

#         Notes:
#         Ensure that all questions are unique and have not been asked before (refer to the history provided).
#         The explanations should be clear and concise, providing context or additional information about the correct answer.
#         Review and format the JSON response to ensure it matches the provided schema.
#         """

#         button = st.sidebar.button('Generate Quiz')

#         if button:
#             if initial_choice == 'Enter the Topic':
#                 if not topic.strip():
#                         st.error("Please enter a topic.")
#                 elif quiz_type == 'Select.....' or quiz_level == 'Select.....' or language == 'Select.....':
#                     st.error("Please select quiz parameters including type, level and language.")
#                 else:                          
#                     response = get_gemini_response(prompt)
#                     try:
#                         all_questions = json.loads(response)
#                         unique_questions = [q for q in all_questions if q not in st.session_state.history]
                        
#                         if len(unique_questions) < num_questions:
#                             st.warning(f"Only {len(unique_questions)} unique questions were generated, but {num_questions} were requested. You may want to reduce the number of questions or try different parameters.")
#                         st.session_state.questions = unique_questions[:num_questions]
#                         st.session_state.history.extend(st.session_state.questions)
#                         st.session_state.user_answers = {f"q{i+1}": None for i in range(len(st.session_state.questions))}
#                     except json.JSONDecodeError:
#                         st.error("Failed to parse the quiz questions. Please try again.")
     

#     # Display Quiz Questions
#     if st.session_state.questions:
#         st.subheader("Quiz Questions")
#         for i, q in enumerate(st.session_state.questions):
#             st.write(f"**Q{i+1}: {q['question']}**")
#             if 'options' in q:
#                 selected_option = st.radio(f"Select an answer for Q{i+1}:", options=q['options'], key=f"q{i+1}")
#             else:
#                 selected_option = st.radio(f"Select True or False for Q{i+1}:", options=['True', 'False'], key=f"q{i+1}")
#             st.session_state.user_answers[f"q{i+1}"] = selected_option
#             st.write("---")

#         if st.button('Submit Answers'):
#             st.subheader("Quiz Results")
#             score = 0
#             for i, q in enumerate(st.session_state.questions):
#                 correct_answer = q['answer']
#                 user_answer = st.session_state.user_answers[f"q{i+1}"]
#                 if user_answer == correct_answer:
#                     score += 1
#                     st.write(f"**Q{i+1}: {q['question']}**")
#                     st.write(f"Your answer: **{user_answer}** - Correct!")
#                 else:
#                     st.write(f"**Q{i+1}: {q['question']}**")
#                     st.write(f"Your answer: **{user_answer}** - Incorrect.")
#                     st.write(f"Correct answer: **{correct_answer}**")
#                 st.write(f"Explanation: {q['explanation']}")
#                 st.write("---")

#             # st.write(f"**Your Score: {score}/{len(st.session_state.questions)}**")
#             st.success(f"Your score is {score}/{len(st.session_state.questions)}!")
# if __name__ == '__main__':
#     main()
