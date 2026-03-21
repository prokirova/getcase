from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from datetime import datetime
import bcrypt

import mysql.connector

def get_server_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password'
    )


def init_db():
    conn = get_server_connection()
    cur = conn.cursor()

    # создаем базу данных, если её нет
    cur.execute("CREATE DATABASE IF NOT EXISTS GetCase")
    cur.execute("USE GetCase")

    # Students
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        skills JSON,
        university VARCHAR(255) NOT NULL,
        faculty VARCHAR(255),
        course TINYINT NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        phone_number VARCHAR(255) NOT NULL UNIQUE,
        tg_id VARCHAR(255) UNIQUE,
        tasks_started JSON,
        tasks_progressing JSON,
        password_hash VARCHAR(255) NOT NULL
    )
    """)

    # Companies
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        information TEXT,
        projects JSON
    )
    """)

    # Cases
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Cases (
        id INT AUTO_INCREMENT PRIMARY KEY,
        organizer_id INT NOT NULL,
        performers JSON,
        description TEXT NOT NULL,
        areas JSON,
        publication_time DATE NOT NULL,
        end_time DATE NOT NULL,
        FOREIGN KEY (organizer_id) REFERENCES Companies(id) ON DELETE RESTRICT ON UPDATE CASCADE
    )
    """)

    conn.commit()
    cur.close()
    conn.close()


app = Flask(__name__, static_folder='static', static_url_path='/static')
#app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_if_not_set')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        university = request.form['university']
        faculty = request.form.get('faculty', '')
        course = request.form['course']
        phone_number = request.form['phone_number']

        # проверки
        if len(password) < 6:
            flash('Пароль должен содержать не менее 6 символов')
            return render_template('register.html')

        try:
            db = get_database()
            cur = db.cursor()

            # проверка на существующий email
            cur.execute("SELECT id FROM Students WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Пользователь с таким email уже существует')
                return render_template('register.html')

            # хеш пароля
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # создание пользователя
            cur.execute("""
                INSERT INTO Students 
                (skills, university, faculty, course, email, phone_number, tg_id, tasks_started, tasks_progressing, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                '[]',  # skills
                university,
                faculty,
                course,
                email,
                phone_number,
                None,  # tg_id
                '[]',  # tasks_started
                '[]',  # tasks_progressing
                password_hash
            ))

            db.commit()
            cur.close()
            db.close()

            flash('Регистрация успешна!')
            return redirect(url_for('login'))

        except Exception as e:
            print(e)
            flash('Ошибка при регистрации')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        """conn = get_db_connection()
        cur = conn.cursor()

        # Ищем пользователя по email
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE email = ?",
            (email,)
        )
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = email
            cur.close()
            conn.close()
            # РЕДИРЕКТ НА ГЛАВНУЮ СТРАНИЦУ (index)
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль')

        cur.close()
        conn.close()"""
        return render_template('login.html')

    return render_template('login.html')

def get_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='GetCase'
    )

def push_to_database(data):
    db = get_database()
    cur = db.cursor()
    command = ("INSERT INTO Companies", "(name,information,projects)")
    if data[0] == "Students":
        command = ("INSERT INTO Students", "(skills, university, faculty, course, email, phone_number, tg_id, tasks_started, tasks_progressing, password_hash)", data[1])
    if data[0] == "Companies":
        command = ("INSERT INTO Companies", "(name,information,projects)")
    if data[0] == "Cases":
        command = ("INSERT INTO Cases", "(organizer_id,performers,description,areas,publication_time,end_time)")
    else:
        return
    if data[0] != "Students" != "Companies" != "Cases":
        return

    cur.execute(command,data[1])
    db.commit()

def update_database(data):
    db = get_database()
    cur = db.cursor()
    Table = data[0]
    changed_columns = data[1]
    new_values = data[2]
    id = data[3]

    if Table !="Students" != "Companies" != "Cases":
        return
    string = ""
    for i in range(len(changed_columns)):
        string += changed_columns[i] + " = " + new_values[i] + ","
    string=string[:-1]
    # if data[0] == "Students":
    #     command = ("UPDATE Students SET skills = %s, university = %s, faculty = %s, course = %s, email = %s, phone_number = %s, tg_id=%s, tasks_started=%s, tasks_progressing=%s, password_hash=%s")
    # if data[0] == "Companies":
    #     command = ("UPDATE Companies SET name = %s, information = %s, projects=%s")
    # if data[0] == "Cases":
    #     command = "UPDATE Cases SET organizer_Id = %s, performers = %s, description = %s, areas = %s, publication_time = %s, end_time =%s"
    command = "UPDATE " + Table + " SET " + string + " WHERE id = " + id
    cur.execute(command)


def pull_database(data):
    db = get_database()
    cur = db.cursor()
    if data[0] != "Students" and data[0] != "Companies" and data[0] != "Cases":
        return
    command = ("SELECT * FROM %s WHERE id = %s")
    #data должна быть (Table, id)
    cur.execute(command, data)
    result = cur.fetchall()
    return result

def date_to_days(date):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    days = year*364+month*30+day
    return days


def get_cases_from_x(Table,id):
    db = get_database()
    cur = db.cursor()
    column = None
    if Table == "Companies":
        column = "Projects"
    if Table == "Students":
        column = "tasks_started"
    if not column:
        return
    command = ("SELECT " + column + " FROM " + Table + " WHERE id = %s")
    cur.execute(command, id)
    result = cur.fetchall()
    result_sorted = sorted(result, key=lambda k: date_to_days(k['end_time']))
    return result_sorted


if __name__ == '__main__':
    app.run()
