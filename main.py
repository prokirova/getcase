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

    # если БД не было - создается
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
        FOREIGN KEY (organizer_id) REFERENCES Companies(id)
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

        # Проверка длины пароля
        if len(password) < 6:
            flash('Пароль должен содержать не менее 6 символов')
            return render_template('register.html')

        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            flash('Пользователь с таким email уже существует')
            cur.close()
            conn.close()
            return render_template('register.html')

        # Хеширование пароля
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Создание пользователя
        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )

        conn.commit()
        cur.close()
        conn.close()"""

        flash('Регистрация успешна! Теперь вы можете войти.')
        return redirect(url_for('login'))

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
    print('Getting database')

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
