# Quiz App Overview

This document outlines the features and functionalities of the Quiz App, designed to generate quizzes based on user inputs and uploaded content.

## Features

- **Quiz Generation**: Users can create quizzes by uploading PDF files, selecting subjects, or entering specific topics.
  
- **Customization Options**:
  - **Number of Questions**: Users can specify how many questions they want in the quiz (1 to 10).
  - **Type of Quiz**: Options include Multiple-Choice and True-False.
  - **Difficulty Level**: Users can choose from Easy, Medium, or Hard.
  - **Language**: Available languages include English, Urdu, and French.

- **Page-Specific Quiz Generation**: Users can upload a PDF file and select specific pages from which the quiz questions should be generated.

## Functionality

1. **Upload Content**: Users can upload a PDF file, and the app will extract text to generate quiz questions based on the content.

2. **Select Specific Pages**: With the `app_pdf_new.py` feature, users can choose specific pages from the uploaded PDF to generate quiz questions focused on that section.

3. **Select Subject**: For quizzes related to Data Science, users can choose from main subjects like Machine Learning, Deep Learning, Mathematics, and Statistics, along with specific sub-fields.

4. **Dynamic Question Generation**: The app utilizes a generative AI model to create unique quiz questions, ensuring that no previously asked questions are repeated.

5. **User Interaction**:
   - Users can answer quiz questions and receive immediate feedback on their performance.
   - The app displays correct answers and explanations for better understanding.

## Technical Details

- **Technologies Used**:
  - **Streamlit**: For building the web application interface.
  - **PyPDF2**: For extracting text from PDF files.
  - **Generative AI Model**: To create quiz questions based on user-defined parameters.
  - **`app_pdf_new.py`**: A module that allows users to select specific pages from a PDF file to generate targeted quiz questions.

## Conclusion

The Quiz App is designed to facilitate learning through interactive quizzes, allowing users to engage with various subjects and topics effectively. By utilizing advanced AI technologies, it provides a seamless experience in quiz generation and assessment.

## Connect with Us

- [LinkedIn](https://www.linkedin.com/in/fmehmood1122/)
- [Facebook](https://www.facebook.com/FMGillani01)
- [Twitter](https://twitter.com/FMGillani)
- [Instagram](https://www.instagram.com/fmgillani/)
