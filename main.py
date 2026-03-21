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
        last_name VARCHAR(255) NOT NULL,
        first_name VARCHAR(255) NOT NULL,
        middle_name VARCHAR(255),
        email VARCHAR(255) NOT NULL UNIQUE,
        phone_number VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        university VARCHAR(255) NOT NULL,
        faculty VARCHAR(255) NOT NULL,
        specialty VARCHAR(255) NOT NULL,
        course TINYINT NOT NULL,
        birthdate DATE NOT NULL,
        skills JSON,
        tg_id VARCHAR(255) UNIQUE,
        tasks_started JSON,
        tasks_progressing JSON
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
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_if_not_set')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name', '')

        email = request.form['email']
        password = request.form['password']

        university = request.form['university']
        faculty = request.form['faculty']
        specialty = request.form['specialty']
        course = int(request.form['course'])

        phone_number = request.form['phone']
        birthdate = request.form['birthdate']

        # проверки
        if len(password) < 6:
            flash('Пароль должен содержать не менее 6 символов')
            return render_template('register.html')

        try:
            db = get_database()
            cur = db.cursor()

            # проверка email
            cur.execute("SELECT id FROM Students WHERE email = %s", (email,))
            if cur.fetchone():
                flash('Пользователь с таким email уже существует')
                return render_template('register.html')

            # проверка телефона
            cur.execute("SELECT id FROM Students WHERE phone_number = %s", (phone_number,))
            if cur.fetchone():
                flash('Пользователь с таким телефоном уже существует')
                return render_template('register.html')

            # хеш пароля
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # вставка
            cur.execute("""
                INSERT INTO Students (
                    last_name, first_name, middle_name,
                    email, phone_number, password_hash,
                    university, faculty, specialty, course,
                    birthdate,
                    skills, tg_id, tasks_started, tasks_progressing
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                last_name,
                first_name,
                middle_name,

                email,
                phone_number,
                password_hash,

                university,
                faculty,
                specialty,
                course,

                birthdate,

                '[]',
                None,
                '[]',
                '[]'
            ))

            #cur.execute("SELECT * FROM Students ORDER BY id DESC LIMIT 1")
            #new_user = cur.fetchone()


            db.commit()
            cur.close()
            db.close()

            flash('Регистрация успешна!')
            return redirect(url_for('login'))

            #return jsonify(new_user)

        except Exception as e:
            print(e)
            flash('Ошибка при регистрации')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            db = get_database()
            cur = db.cursor(dictionary=True)

            # ищем пользователя
            cur.execute("SELECT * FROM Students WHERE email = %s", (email,))
            user = cur.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # сохраняем в сессию
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['name'] = user['first_name']

                cur.close()
                db.close()

                #return redirect(url_for('index'))
                return redirect(url_for('profile'))
            else:
                flash('Неверный email или пароль')

            cur.close()
            db.close()

        except Exception as e:
            print(e)
            flash('Ошибка при входе')

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


import json

@app.route('/profile')
def profile():
    # проверка: залогинен ли пользователь
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        db = get_database()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT * FROM Students WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()

        cur.close()
        db.close()

        if not user:
            flash('Пользователь не найден')
            return redirect(url_for('index'))

        # формируем данные под HTML
        user_data = {
            "full_name": f"{user['last_name']} {user['first_name']} {user['middle_name'] or ''}",
            "first_name": user['first_name'],
            "username": user['email'].split('@')[0],  # временно
            "email": user['email'],
            "phone": user['phone_number'],
            "telegram": user['tg_id'],
            "university": user['university'],
            "institute": user['faculty'],  # у тебя faculty = институт
            "specialty": user['specialty'],
            "course": user['course'],
            "degree": "бакалавриат",  # пока заглушка
            "skills": json.loads(user['skills']) if user['skills'] else [],
            "avatar_url": None
        }

        return render_template('profile.html', user=user_data)

    except Exception as e:
        print(e)
        flash('Ошибка при загрузке профиля')
        return redirect(url_for('index'))


@app.route('/case/<int:case_id>')
def view_case(case_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('view_case.html', case_id=case_id)


@app.route('/api/cases/<int:case_id>', methods=['GET'])
def get_case_api(case_id):
    if 'user_id' not in session:
        return jsonify({"error": "Not authorized"}), 401

    try:
        db = get_database()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT c.*, comp.name AS company_name
            FROM Cases c
            LEFT JOIN Companies comp ON c.organizer_id = comp.id
            WHERE c.id = %s
        """, (case_id,))

        case = cur.fetchone()

        cur.close()
        db.close()

        if not case:
            return jsonify({"error": "Case not found"}), 404

        return jsonify(case)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/cases')
def all_cases():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('cases.html')


@app.route('/api/cases', methods=['GET'])
def get_cases_api():
    if 'user_id' not in session:
        return jsonify({"error": "Not authorized"}), 401

    try:
        db = get_database()
        cur = db.cursor(dictionary=True)

        cur.execute("""
            SELECT c.*, comp.name AS company_name
            FROM Cases c
            LEFT JOIN Companies comp ON c.organizer_id = comp.id
            ORDER BY c.publication_time DESC
        """)

        cases = cur.fetchall()

        cur.close()
        db.close()

        return jsonify(cases)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
