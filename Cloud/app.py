# app.py
from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image
import pytesseract
import openai
import pandas as pd

app = Flask(__name__)
app.secret_key = ''  # Replace with a strong and unique secret key

# Set your OpenAI API key
openai.api_key = ''  # Replace with your OpenAI API key

@app.route('/')
def index():
    # Initialize a variable to store the teacher's answer
    session['teacher_answer'] = session.get('teacher_answer', None)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'studentImage' not in request.files:
        return "No file part"

    student_file = request.files['studentImage']

    if student_file.filename == '':
        return "No selected file"

    # Extract information from student image
    student_info = extract_information(student_file)

    if not session['teacher_answer']:
        # If teacher's answer is not stored, request teacher's answer
        return render_template('upload_teacher.html', student_info=student_info)
    else:
        # If teacher's answer is available, perform comparison
        teacher_info = {'name': 'Teacher', 'question_number': student_info['question_number'], 'text': session['teacher_answer']}
        analysis = compare_and_analyze(student_info, teacher_info)
        # Append the results to the Excel sheet
        append_to_excel(student_info, analysis)
        return render_template('result.html', result_message="Analysis completed and saved to Excel.")

@app.route('/upload_teacher', methods=['POST'])
def upload_teacher():
    if 'teacherImage' not in request.files:
        return "No file part"

    teacher_file = request.files['teacherImage']

    if teacher_file.filename == '':
        return "No selected file"

    # Process the teacher image using Tesseract OCR
    teacher_text = perform_ocr(teacher_file)

    # Store the teacher's answer in the session
    session['teacher_answer'] = teacher_text

    # Redirect back to the upload page for the student's answer
    return redirect(url_for('upload'))

def extract_information(image_file):
    # Use Tesseract to perform OCR on the image file
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)

    # Extract relevant information (you might need to adjust this based on your image format)
    lines = text.split('\n')

    # Check if there are at least two lines in the OCR result
    if len(lines) >= 2:
        name = lines[0].strip()
        question_number = lines[1].strip()
        return {'name': name, 'question_number': question_number, 'text': text}
    else:
        # Handle the case where there are not enough lines in the OCR result
        return {'name': 'Unknown', 'question_number': 'Unknown', 'text': text}

def compare_and_analyze(student_info, teacher_info):
    student_answer = student_info['text']
    teacher_answer = teacher_info['text']

    # Check if the answers are subjective or objective
    if is_subjective(student_answer) and is_subjective(teacher_answer):
        # Use ChatGPT for subjective comparison
        input_text = f"Student Answer: {student_answer}\nTeacher Answer: {teacher_answer}"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=input_text,
            max_tokens=100
        )
        similarity_score = response['choices'][0]['text']
        analysis = {'type': 'Subjective', 'similarity_score': similarity_score}
    elif is_objective(student_answer) and is_objective(teacher_answer):
        # Compare objective answers
        is_correct = compare_objective_answers(student_answer, teacher_answer)
        analysis = {'type': 'Objective', 'is_correct': is_correct}
    else:
        analysis = {'type': 'Mixed', 'message': 'Mixed types of answers detected. Manual review required.'}

    return analysis

def is_subjective(answer):
    # Implement logic to determine if an answer is subjective based on keywords
    # You might need to customize this based on your specific criteria
    subjective_keywords = ['What is', 'Explain', 'Describe']
    return any(keyword in answer for keyword in subjective_keywords)

def is_objective(answer):
    # Implement logic to determine if an answer is objective based on keywords or format
    # For example, checking for "true" or "false" or numeric values
    return answer.lower() in ['true', 'false'] or answer.strip().isdigit()

def compare_objective_answers(student_answer, teacher_answer):
    # Implement logic to compare objective answers
    return student_answer.strip().lower() == teacher_answer.strip().lower()

def append_to_excel(student_info, analysis):
    # Create a DataFrame for the new entry
    entry = pd.DataFrame({
        'Name of Student': [student_info['name']],
        'Number of Q': [student_info['question_number']],
        'Analysis Type': [analysis['type']],
    })

    # Add additional columns based on the type of analysis
    if analysis['type'] == 'Subjective':
        entry['Score'] = [analysis['similarity_score']]
    elif analysis['type'] == 'Objective':
        entry['Is Correct'] = [analysis['is_correct']]
    else:
        entry['Message'] = [analysis['message']]

    # Load existing Excel file or create a new one
    try:
        df = pd.read_excel('evaluation_report.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Name of Student', 'Number of Q', 'Analysis Type', 'Score', 'Is Correct', 'Message'])

    # Append the new entry to the DataFrame
    df = df.append(entry, ignore_index=True)

    # Save the updated DataFrame back to the Excel file
    df.to_excel('evaluation_report.xlsx', index=False)

if __name__ == '__main__':
    app.run(debug=True)
