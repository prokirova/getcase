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
    if data[0] == "student":
        command = ("INSERT INTO Students", "(skills, university, faculty, course, email, phone_number, tg_id, tasks_started, tasks_progressing, password_hash)", data[1])
    if data[0] == "company":
        command = ("INSERT INTO Companies", "(name,information,projects)", data[1])
    if data[0] == "case":
        command = ("INSERT INTO Cases", "(organizer_id,performers,description,areas,publication_time,end_time)", data[1])
    cur.execute(command)
    db.commit()

def update_database(data):
    db = get_database()
    cur = db.cursor()
    command = ("UPDATE %s SET  WHERE id = ?", data[1], data[0])


def pull_database(data):
    db = get_database()
    cur = db.cursor()
    command = ("SELECT * FROM %s WHERE id = ?", data[1])
    cur.execute(command, data[0])
    result = cur.fetchall()
    return result

def get_cases_from_user(user):
    db = get_database()
    cur = db.cursor()


if __name__ == '__main__':
    app.run()
