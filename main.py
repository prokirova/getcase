from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import os
from datetime import datetime
import bcrypt



app = Flask(__name__, static_folder='static', static_url_path='/static')
#app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key_if_not_set')
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
