from flask import Flask, render_template, request, session, redirect, url_for, flash
from utils import *
import db as db
# from google_ocr import detect_text
from ocr_space import ocr_space_text_extraction as detect_text
import os
from flask import send_from_directory


app = Flask(__name__)
app.secret_key = 'secret'
@app.route('/uploads/<path:student_image>')
def uploaded_file(student_image):
    return send_from_directory('uploads', student_image)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    student_file = request.files.get('image')
    student_name = request.form.get('studentName')
    if not student_file:
        flash('Please upload the student\'s answer.', 'danger')
        return render_template('upload_student.html')

    file_path = f"uploads/{student_file.filename}"
    student_file.save(file_path)
    student_text = detect_text(file_path)
    result = search_que_and_answer_in_text(student_text)


    score = get_similarity_score(result['answer'], session['teacher_answer'])

    
    append_to_excel({'name': student_name, 'question': result['question'], 'answer': result['answer']}, session['teacher_answer'], score)
    flash("Analysis completed and saved to Excel.", "success")
    return redirect(url_for('upload_student'))


# @app.route('/history')
# def history():
#     search_hist = db.get_search_history()
#     history = []
#     for hist in search_hist:
#         history.append({'student_name': hist[2], 'question': hist[3], 'result': hist[4], 'time': hist[5]})
#     return render_template('history.html', histories=history)


@app.route('/upload_student')
def upload_student():
    if not session.get('teacher_answer'):
        flash('Please upload the teacher\'s answer first.', 'danger')
        return redirect(url_for('index'))
    return render_template('upload_student.html')


@app.route('/upload_teacher', methods=['POST'])
def upload_teacher():
    teacher_file = request.files.get('image')
    if not teacher_file:
        flash('Please upload the teacher\'s answer.', 'danger')
        return render_template('upload_teacher.html')

    file_path = f"uploads/{teacher_file.filename}"
    teacher_file.save(file_path)
    teacher_text = detect_text(file_path)
    result = search_que_and_answer_in_text(teacher_text)
    

    session['teacher_answer'] = result['answer']
    session['teacher_question'] = result['question']

    flash('Teacher\'s answer uploaded successfully.', 'success')
    return redirect(url_for('upload_student'))

# @app.route('/search_student', methods=['POST'])
# def search_student():
#     student_name = request.form.get('studentSearch')

#     try:
#         # Fetch student information from the 'evaluation_report.xlsx' file
#         students_df = pd.read_excel('evaluation_report.xlsx')
#         student_info = students_df[students_df['Name of Student'] == student_name].iloc[0]  # Assuming unique names
#         extracted_text = student_info['Extracted Answer']

#         # Get the path to the image based on student name (assuming the image name matches the student name)
#         image_path = os.path.join('uploads', f'{student_name}.jpg')  # Adjust the file extension if different
#         # Check if the image file exists
#         if os.path.exists(image_path):
#             student_image = image_path  # Use the image pat
#             # student_image = image_path.replace('\\', '/')
#         else:
#             student_image = None  # Handle the case where the image doesn't exist

#         # Fetch previous reviews for the student (if available)
#         previous_reviews = []  # Fetch reviews related to the student from another data source or database

#         return render_template('review_student.html', student_name=student_name, extracted_text=extracted_text,
#                                student_image=student_image, previous_reviews=previous_reviews)
#     except Exception as e:
#         # Handle exceptions (e.g., file not found, invalid data, etc.)
#         print(f"Error: {e}")
#         flash('An error occurred while retrieving student information.', 'danger')
#         return redirect(url_for('upload_student'))
# @app.route('/review_student', methods=['POST'])
@app.route('/review_student', methods=['POST'])
def review_student():
    student_name = request.form.get('studentSearch')

    try:
        students_df = pd.read_excel('evaluation_report.xlsx')
        student_info = students_df[students_df['Name of Student'] == student_name]

        if not student_info.empty:
            student_info = student_info.iloc[0]
            extracted_text = student_info['Extracted Answer']

            image_path = os.path.join('uploads', f'{student_name}.jpg')  # Adjust file extension if different
            if os.path.exists(image_path):
                student_image = student_name + '.jpg'  # Construct the image path correctly
            else:
                student_image = None

            previous_reviews = []  # Fetch reviews related to the student from another data source or database

            return render_template('review_student.html', student_name=student_name, extracted_text=extracted_text,
                                   student_image=student_image, previous_reviews=previous_reviews)
        else:
            flash('Student information not found.', 'danger')
            return redirect(url_for('upload_student'))

    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while retrieving student information.', 'danger')
        return redirect(url_for('upload_student'))


@app.route('/submit_review', methods=['POST'])
def submit_review():
    if request.method == 'POST':
        student_name = request.form.get('studentName')
        rating = request.form.get('rating')  # Get the selected rating value
        review_comment = request.form.get('reviewComment')

        # Save the student's name and comment to a text file
        with open('review_comments.txt', 'a') as file:
            file.write(f"Student Name: {student_name}\n Rating: {rating}\n Review Comment: {review_comment}\n \n")

        # Perform other actions or redirections if needed
        return redirect(url_for('upload_student'))  # Redirect to the index or another appropriate page


if __name__ == '__main__':
    app.run(debug=True)