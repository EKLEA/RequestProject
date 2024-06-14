import os
import json
import secrets
from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd

app = Flask(__name__)

# Генерация случайного ключа
app.secret_key = os.urandom(24)

# MongoDB подключение
app.config['MONGO_URI'] = 'mongodb://localhost:27017/admin'

# MongoDB
mongo = PyMongo(app)

# группа пользователей
ADMINS ="ADMINS"
REQUESTs ="Requests"
adminsTypes= ["GlAdmin" , "Admin"]


@app.route('/')
def login():
    return render_template('index.html')

@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form['username']
    password = request.form['password']

    # Поиск пользователя
    user = mongo.db[ADMINS].find_one({'username': username})

    print("hello")
    if user and user['password'] == password: #хэш пароль потом вернуть
        session['username'] = user['username']
        if user.get('role') == adminsTypes[1]:
            return redirect(url_for('dashboard'))
        elif user.get('role') == adminsTypes[0]:
            return redirect(url_for('dashboardAdmin'))


    else:
        return "Вход не удался! Пожалуйста, проверьте свое имя пользователя и пароль."

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    generated_password = secrets.token_urlsafe(12)

    if request.method == 'POST':
        user_data = {
            'request_number': request.form['request_number'],
            'full_name': request.form['full_name'],
            'phone': request.form['phone'],
            'ssid': request.form['ssid'],
            'login': request.form['login'],
            'password': request.form['password'],  # Внимание: Не храните пароль в открытом виде
            'message': f"Ваш персональный пароль для подключения к сети {request.form['ssid']} : {generated_password}",
            'username': session.get('username')
        }

        # Добавление заявки в базу данных
        mongo.db.requests.insert_one(user_data)

        # Получение списка выбранных заявок
        selected_requests = request.form.getlist('selected_requests')
        if selected_requests:
            # Удаление выбранных заявок из базы данных
            mongo.db.requests.delete_many({'_id': {'$in': selected_requests}})

    user_requests = list(mongo.db.requests.find({}))  # Получаем все заявки из базы данных

    return render_template('dashboard.html', username=username, user_requests=user_requests, generated_password=generated_password)
@app.route('/dashboardAdmin', methods=['GET', 'POST'])
def dashboardAdmin():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    generated_password = secrets.token_urlsafe(12)

    if request.method == 'POST':
        user_data = {
            'request_number': request.form['request_number'],
            'full_name': request.form['full_name'],
            'phone': request.form['phone'],
            'ssid': request.form['ssid'],
            'login': request.form['login'],
            'password': request.form['password'],  # Внимание: Не храните пароль в открытом виде
            'message': f"Ваш персональный пароль для подключения к сети {request.form['ssid']} : {generated_password}",
            'username': session.get('username')
        }

        # Добавление заявки в базу данных
        mongo.db.requests.insert_one(user_data)

        # Получение списка выбранных заявок
        selected_requests = request.form.getlist('selected_requests')
        if selected_requests:
            # Удаление выбранных заявок из базы данных
            mongo.db.requests.delete_many({'_id': {'$in': selected_requests}})

    user_requests = list(mongo.db.requests.find({}))  # Получаем все заявки из базы данных

    return render_template('dashboardAdmin.html', username=username, user_requests=user_requests, generated_password=generated_password)


if __name__ == '__main__':
    app.run()
