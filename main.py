from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from datetime import datetime
import bcrypt
from werkzeug.utils import secure_filename

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
UPLOAD_FOLDER = 'solutions'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'zip', 'rar', 'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 102
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
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

# тестовая генерация данных для кейсов
def generate_artificial_cases():
    db = get_database()
    cur = db.cursor()

    try:
        # проверка наличия компаний для кейсов
        cur.execute("SELECT COUNT(*) FROM Companies")
        count = cur.fetchone()[0]

        if count == 0:
            cur.executemany("""
                INSERT INTO Companies (name, information, projects)
                VALUES (%s, %s, %s)
            """, [
                ("Yandex", "Tech ecosystem", "[]"),
                ("Ozon", "Marketplace platform", "[]"),
                ("Sber", "Banking and tech", "[]")
            ])
            db.commit()

        # получение ID компаний
        cur.execute("SELECT id FROM Companies LIMIT 3")
        companies = cur.fetchall()

        if len(companies) < 3:
            print("Недостаточно компаний")
            return

        c1, c2, c3 = [c[0] for c in companies]

        # добавление кейсов
        cur.executemany("""
            INSERT INTO Cases (
                organizer_id,
                performers,
                description,
                areas,
                publication_time,
                end_time
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [
            (
                c1,
                '[]',
                "Разработка рекомендательной системы для пользователей",
                '["ML", "Python"]',
                "2025-03-01",
                "2025-04-01"
            ),
            (
                c2,
                '[]',
                "Оптимизация UX корзины маркетплейса",
                '["Frontend", "UX"]',
                "2025-03-05",
                "2025-04-10"
            ),
            (
                c3,
                '[]',
                "Анализ пользовательских данных и сегментация",
                '["Data Science"]',
                "2025-03-10",
                "2025-04-15"
            )
        ])

        db.commit()
        print("Тестовые кейсы успешно добавлены")

    except Exception as e:
        print("Ошибка при заполнении:", e)

    finally:
        cur.close()
        db.close()


# ИСПОЛЬЗОВАТЬ ОСОБО ОСТОРОЖНО
# тестовая очистка данных кейсов и компаний из БД
def clear_test_data():
    db = get_database()
    cur = db.cursor()

    try:
        # удаление кейсов
        cur.execute("DELETE FROM Cases")

        # удаление компаний
        cur.execute("DELETE FROM Companies")

        db.commit()
        print("Тестовые данные удалены")

    except Exception as e:
        print("Ошибка при очистке:", e)

    finally:
        cur.close()
        db.close()

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

    return render_template('case.html', case_id=case_id)


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

@app.route('/my_cases')
def my_cases():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        db = get_database()
        cur = db.cursor(dictionary=True)

        # получаем пользователя
        cur.execute("SELECT tasks_started FROM Students WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()

        #case_ids = json.loads(user['tasks_started']) if user['tasks_started'] else []
        raw_tasks = user['tasks_started']

        if not raw_tasks:
            case_ids = []
        elif isinstance(raw_tasks, str):
            case_ids = json.loads(raw_tasks)
        else:
            case_ids = raw_tasks

        if not case_ids:
            return render_template('my_cases.html', cases=[])

        # получаем сами кейсы
        format_strings = ','.join(['%s'] * len(case_ids))
        cur.execute(f"""
            SELECT c.*, comp.name AS company_name
            FROM Cases c
            LEFT JOIN Companies comp ON c.organizer_id = comp.id
            WHERE c.id IN ({format_strings})
        """, tuple(case_ids))

        cases = cur.fetchall()

        print(user['tasks_started'], type(user['tasks_started']))

        cur.close()
        db.close()

        return render_template('my_cases.html', cases=cases)

    except Exception as e:
        print(e)
        return "Ошибка"

@app.route('/api/join_case/<int:case_id>', methods=['POST'])
def join_case(case_id):
    if 'user_id' not in session:
        return jsonify({"error": "Не авторизован"}), 401

    try:
        db = get_database()
        cur = db.cursor(dictionary=True)

        cur.execute("SELECT tasks_started FROM Students WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404

        tasks = json.loads(user['tasks_started'] or '[]')

        already_participating = case_id in tasks

        if not already_participating:
            tasks.append(case_id)
            cur.execute(
                "UPDATE students SET tasks_started = %s WHERE id = %s",
                (json.dumps(tasks), session['user_id'])
            )
            db.commit()
            message = "Вы успешно записались"
        else:
            message = "Вы уже участвуете"

        cur.close()
        db.close()

        return jsonify({
            "success": True,
            "message": message,
            "already_participating": already_participating
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500



@app.route('/api/submit_solution', methods=['POST'])
def submit_solution():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Файл не найден"}), 400

    file = request.files['file']
    case_id = request.form.get('case_id')

    if not case_id:
        return jsonify({"success": False, "error": "case_id обязателен"}), 400

    if file.filename == '':
        return jsonify({"success": False, "error": "Файл не выбран"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Можно сделать уникальное имя, например: user_id + case_id + timestamp
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"case_{case_id}_{filename}")
        file.save(save_path)
        return jsonify({"success": True, "message": "Файл загружен"})

    return jsonify({"success": False, "error": "Недопустимый формат файла"}), 400

@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({"error": "Not authorized"}), 401

    try:
        data = request.json

        phone = data.get('phone')
        telegram = data.get('telegram')
        skills = data.get('skills')

        db = get_database()
        cur = db.cursor()

        cur.execute("""
        UPDATE Students SET
            university=%s,
            faculty=%s,
            specialty=%s,
            course=%s,
            email=%s,
            phone_number=%s,
            tg_id=%s,
            skills=%s
        WHERE id=%s
        """, (
            data['university'],
            data['faculty'],
            data['specialty'],
            int(data['course']),
            data['email'],
            data['phone'],
            data['tg_id'],
            json.dumps(data['skills']),
            session['user_id']
        ))

        db.commit()
        cur.close()
        db.close()

        return jsonify({"success": True})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/participation_status/<int:case_id>', methods=['GET'])
def participation_status(case_id):
    if 'user_id' not in session:
        return jsonify({"participates": False})

    db = get_database()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT tasks_started FROM Students WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    if not user:
        print("Пользователь не найден в базе")
        return jsonify({"participates": False})

    raw_tasks = user['tasks_started']


    tasks = json.loads(raw_tasks) if raw_tasks and raw_tasks.strip() else []

    try:
        tasks_int = [int(item) for item in tasks]
        participates = case_id in tasks_int
    except ValueError:
        participates = False


    cur.close()
    db.close()

    return jsonify({"participates": participates})


@app.route('/logout')
def logout():
    session.clear()  # очищаем всю сессию
    flash('Вы вышли из аккаунта')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    # Функция создания искусственных кейсов
    # в БД для тестра размещения данных
    # generate_artificial_cases()

    # удаление для тестовых данных кейсов и компаний
    # ИСПОЛЬЗОВАТ ОСОБО ОСТОРОЖНО
    # clear_test_data()

    app.run(debug=True)
