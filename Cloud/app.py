from flask import Flask, render_template, request
from PIL import Image
import pytesseract
import openai

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = ''

def perform_ocr(image_file):
    # Use Tesseract to perform OCR on the image file
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    # Only return text after the first line
    return '\n'.join(text.split('\n')[1:])

def extract_question_info(extracted_text):
    # Extract question number assuming it's on the first line
    question_number = extracted_text.split(':', 1)[0][1:].strip()
    return question_number, extracted_text

def is_subjective_question(answer_type):
    # Check if the question is subjective based on keywords
    subjective_keywords = ['What is', 'Explain', 'Describe']
    return any(keyword in answer_type for keyword in subjective_keywords)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'studentImage' not in request.files or 'teacherImage' not in request.files:
        return "No file part"

    student_file = request.files['studentImage']
    teacher_file = request.files['teacherImage']

    if student_file.filename == '' or teacher_file.filename == '':
        return "No selected file"

    # Process the student image using Tesseract OCR
    student_text = perform_ocr(student_file)

    # Process the teacher image using Tesseract OCR
    teacher_text = perform_ocr(teacher_file)

    # Extract question number and answer type
    question_number, extracted_text = extract_question_info(student_text)
    answer_type = 'subjective' if is_subjective_question(extracted_text) else 'objective'

    if answer_type == 'subjective':
        # Use ChatGPT for subjective comparison
        similarity_score = compare_with_chatgpt(student_text, teacher_text)
        result_message = f"Subjective Question {question_number} Similarity Score: {similarity_score}"
    else:
        # Compare objective answers
        is_correct = compare_objective_answers(extracted_text, teacher_text)
        result_message = f"Objective Question {question_number} Correct: {is_correct}"

    return render_template('result.html', result_message=result_message)

def compare_with_chatgpt(student_answer, teacher_answer):
    # Use ChatGPT for subjective comparison
    # For simplicity, concatenate student and teacher answers for comparison
    input_text = f"Student Answer: {student_answer}\nTeacher Answer: {teacher_answer}"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=input_text,
        max_tokens=100
    )
    return response['choices'][0]['text']

def compare_objective_answers(student_answer, teacher_answer):
    # Implement logic to compare objective answers
    # For simplicity, assuming a simple string comparison
    return student_answer.strip().lower() == teacher_answer.strip().lower()

if __name__ == '__main__':
    app.run(debug=True)
