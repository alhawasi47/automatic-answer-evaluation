import sqlite3


DATABASE = 'db.sqlite3'


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image TEXT NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image TEXT NOT NULL,
                student_name TEXT NOT NULL,
                student_answer TEXT NOT NULL,
                question TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


def insert_answer(image, question_text, answer_text):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO answers (image, question_text, answer_text)
            VALUES (?, ?, ?)
        ''', (image, question_text, answer_text))
        conn.commit()


def insert_search_history(image, student_name, student_answer, question, result):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO search_history (image, student_name, student_answer, question, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (image, student_name, student_answer, question, result))
        conn.commit()


def get_answers():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM answers
        ''')
        return cursor.fetchall()


def get_search_history():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM search_history
        ''')
        return cursor.fetchall()
