from flask import Flask, render_template, request
from google.cloud import vision
from google.cloud.vision_v1 import types  # Modified import
import openai

app = Flask(__name__)

# Set your Google Cloud Vision API credentials and OpenAI API key
# Replace 'YOUR_GOOGLE_API_KEY' and 'YOUR_OPENAI_API_KEY' with your actual keys
google_api_key = ''
openai.api_key = ''

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


    # Process the image using Google Cloud Vision API
    client = vision.ImageAnnotatorClient()
    image_content = student_file.read()
    image = types.Image(content=image_content)  # Modified import

    response = client.text_detection(image=image)
    texts = response.text_annotations

    extracted_text = ""
    for text in texts:
        extracted_text += text.description + '\n'

    # Extract question number and answer type (subjective or objective)
    question_number, answer_type = extract_question_info(extracted_text)

    if answer_type == 'subjective':
        # Use ChatGPT for subjective comparison
        teacher_answer = get_teacher_answer(question_number)
        similarity_score = compare_with_chatgpt(extracted_text, teacher_answer)
        result_message = f"Subjective Question {question_number} Similarity Score: {similarity_score}"
    elif answer_type == 'objective':
        # Compare objective answers
        teacher_answer = get_teacher_answer(question_number)
        is_correct = compare_objective_answers(extracted_text, teacher_answer)
        result_message = f"Objective Question {question_number} Correct: {is_correct}"
    else:
        result_message = "Invalid question or answer type"

    return render_template('result.html', result_message=result_message)

def extract_question_info(extracted_text):
    # Implement logic to extract question number and answer type
    # You might need to customize this based on the format of your questions
    # For simplicity, assuming question format like "Q1: What is ...?"
    question_parts = extracted_text.split(':', 1)
    question_number = question_parts[0][1:].strip()  # Extract question number
    answer_type = 'subjective' if 'What is' in question_parts[1] else 'objective'
    return question_number, answer_type

def get_teacher_answer(question_number):
    # Implement logic to retrieve the teacher's answer for a given question number
    # For simplicity, assuming the teacher's answers are stored in a dictionary
    teacher_answers = {
        '1': 'The correct answer for objective question 1',
        '2': 'The correct answer for objective question 2',
        'subjective_1': 'The teacher\'s subjective answer for question 1'
    }
    return teacher_answers.get(question_number, '')

def compare_objective_answers(student_answer, teacher_answer):
    # Implement logic to compare objective answers
    # For simplicity, assuming a simple string comparison
    return student_answer.strip().lower() == teacher_answer.strip().lower()

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

if __name__ == '__main__':
    app.run(debug=True)
