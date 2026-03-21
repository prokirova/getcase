import mysql
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from datetime import datetime
import bcrypt
import mysql.connector as connector


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
        command = ("INSERT INTO Students", data[1], data[2])
    if data[0] == "company":
        command = ("INSERT INTO Companies", data[1], data[2])
    if data[0] == "case":
        command = ("INSERT INTO Cases", data[1], data[2])
    cur.execute(command)
    db.commit()

def pull_database(data):


if __name__ == '__main__':
    app.run()
