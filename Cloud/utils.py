from PIL import Image
import pandas as pd
import re
import openai
import os
import json


openai.api_key = ""

os.environ['OPENAI_API_KEY'] = ""


def extract_information(image_file):
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)

    lines = text.split('\n')

    if len(lines) >= 2:
        name = lines[0].strip()
        question_number = lines[1].strip()
        return {'name': name, 'question_number': question_number, 'text': text}
    else:
        return {'name': 'Unknown', 'question_number': 'Unknown', 'text': text}


def compare_and_analyze(student_info, teacher_info):
    student_answer = student_info['text']
    teacher_answer = teacher_info['text']

    if is_subjective(student_answer) and is_subjective(teacher_answer):
        input_text = f"Student Answer: {student_answer}\nTeacher Answer: {teacher_answer}"
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=input_text,
            max_tokens=100
        )
        similarity_score = response['choices'][0]['text']
        analysis = {'type': 'Subjective', 'similarity_score': similarity_score}
    elif is_objective(student_answer) and is_objective(teacher_answer):
        is_correct = compare_objective_answers(student_answer, teacher_answer)
        analysis = {'type': 'Objective', 'is_correct': is_correct}
    else:
        analysis = {'type': 'Mixed',
                    'message': 'Mixed types of answers detected. Manual review required.'}

    return analysis


def is_subjective(answer):
    subjective_keywords = ['What is', 'Explain', 'Describe']
    return any(keyword in answer for keyword in subjective_keywords)


def is_objective(answer):
    return answer.lower() in ['true', 'false'] or answer.strip().isdigit()


def compare_objective_answers(student_answer, teacher_answer):
    return student_answer.strip().lower() == teacher_answer.strip().lower()


def append_to_excel(student_info, teacher_answer, score):
    entry = pd.DataFrame({
        'Name of Student': [student_info['name']],
        'Extracted Question': [student_info['question']],
        'Extracted Answer': [student_info['answer']],
        'Teacher Answer': [teacher_answer],
        'Score': [score]
    })

    try:
        df = pd.read_excel('evaluation_report.xlsx')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Name of Student', 'Extracted Question',
                          'Extracted Answer', 'Teacher Answer', 'Score'])

    # add the new entry to the DataFrame
    df = pd.concat([df, entry], ignore_index=True)

    df.to_excel('evaluation_report.xlsx', index=False)


def get_similarity_score(student_answer, teacher_answer):
    prompt = f"Compare the similarity in meaning between the student's answer and the teacher's answer on a scale from 0 to 5. Only respond in number without any textual context. \n Student Answer: '{student_answer}' \n Teacher Answer: '{teacher_answer}'"

    client = openai.Client()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Updated model name
        messages=[{
            "role":"user",
            "content": prompt,
        }]
    )

    with open('response.json', 'w') as f:
        f.write(str(response))

    # Extract and print the generated response
    generated_response = response.choices[0]
    print("Generated Response:", generated_response.message.model_dump_json())

    # Parse the response to extract the similarity score
    try:
        similarity_score = json.loads(generated_response.message.model_dump_json())
        return similarity_score.get("content")
    except ValueError:
        print("Unable to extract similarity score.")
        return None


def search_que_and_answer_in_text(text):
    question_pattern = re.compile(r'(Q\d+\).+?)(?=Q\d+|$)', re.DOTALL)
    matches = re.findall(question_pattern, text)
    result = {}
    for match in matches:
        split_text = match.strip().split('\n', 1)
        result['question'] = split_text[0]
        result['answer'] = split_text[1]

    return result
# def save_feedback_to_excel(feedback_data):
#     try:
#         # Read existing feedback from the Excel file (if it exists)
#         existing_feedback = pd.read_excel('feedback.xlsx')
        
#         # Append new feedback to the existing data
#         feedback_df = pd.DataFrame([feedback_data])
#         updated_feedback = pd.concat([existing_feedback, feedback_df], ignore_index=True)
        
#         # Save the updated feedback data back to the Excel file
#         updated_feedback.to_excel('feedback.xlsx', index=False)
#     except FileNotFoundError:
#         # If the file doesn't exist, create a new file and save the feedback data
#         feedback_df = pd.DataFrame([feedback_data])
#         feedback_df.to_excel('feedback.xlsx', index=False)
