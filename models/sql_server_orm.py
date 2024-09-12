import pyodbc
import bcrypt
import base64
import asyncio

def connect_to_db():
    DRIVER = '{ODBC Driver 17 for SQL Server}'
    SERVER = '.'
    DATABASE = 'Flask'
    conn = pyodbc.connect(f'DRIVER={DRIVER};' +
                          f'SERVER={SERVER};' +
                          f'DATABASE={DATABASE};' +
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()
    return conn,cursor

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return base64.b64encode(hashed_password).decode('utf-8')

def verify_password(stored_password, entered_password):
    stored_password_bytes = base64.b64decode(stored_password)
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_password_bytes)

def search_user(username):
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    try :
        username, instagram_id, password = cursor.fetchone()
        conn.close()
        return {'username': username, 'instagram_id': instagram_id, 'password': password}
    except TypeError:
        conn.close()
        return dict()


def create_user(username, instagram_id,password):
    conn,cursor = connect_to_db()
    hashed_password = hash_password(password)
    cursor.execute("""
    INSERT INTO users (username, instagram_id, password) VALUES (?, ?, ?)
    """,(username, instagram_id, hashed_password,))
    conn.commit()
    conn.close()


def add_question(question_title, question_body, username):
    conn, cursor = connect_to_db()
    query = """
    INSERT INTO questions (id, questionTitle, questionText, askedByUsername)
    VALUES (newid(), ?, ?, ?)
    """
    cursor.execute(query, (question_title, question_body, username))
    conn.commit()
    conn.close()

def get_questions():
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM Flask..questions")
    return cursor.fetchall()

def get_answers(question_id):
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM Flask..answers WHERE questionId = ?", (question_id,))
    return cursor.fetchall()


def add_answer(question_id, answered_username, answer):
    conn, cursor = connect_to_db()
    cursor.execute("""
        INSERT INTO Flask..answers (id, questionId, answeredByUsername, answer)
        VALUES (NEWID(), ?, ?, ?)
    """, (question_id, answered_username, answer))
    conn.commit()
    conn.close()

def search_question(text):
    conn, cursor = connect_to_db()
    cursor.execute("SELECT * FROM Flask..questions WHERE questionText LIKE N'%{}%'".format(text))
    return cursor.fetchall()

def add_rating(score, question_id, user_id,):
    """
    [id],[score],[questionId],[userId]
    :return: None
    """
    conn, cursor = connect_to_db()
    cursor.execute("insert into Flask..answersRating VALUES (NEWID(),?,?,?)",
                   (score, question_id, user_id,))
    conn.commit()
    conn.close()


def get_top_users():
    conn, cursor = connect_to_db()
    cursor.execute("""SELECT userId, SUM(score) AS score
                        FROM Flask..[answersRating]
                        GROUP BY userId
                        ORDER BY score DESC;""")
    return cursor.fetchall()

