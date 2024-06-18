import os
import json
import secrets

from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
import re
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
ADMINS = "ADMINS"
REQUESTS = "Requests"
adminsTypes = ["Главный", "Не главный"]

def validate_phone_number(phone):
    pattern = re.compile(r'^(\+7|8)?\d{10}$')
    return pattern.match(phone)
@app.route('/')
def login():
    return render_template('index.html')


@app.route('/check_login', methods=['POST'])
def check_login():
    admin_login = request.form['username']
    password = request.form['password']

    # Поиск пользователя
    user = mongo.db[ADMINS].find_one({'admin_login': admin_login})
    if user and user['admin_password'] == password:  # хэш пароль потом вернуть
        session['username'] = user['admin_login']
        if user.get('admin_type') == adminsTypes[1]:
            return redirect(url_for('dashboard'))
        elif user.get('admin_type') == adminsTypes[0]:
            return redirect(url_for('dashboardAdmin'))


    else:
        return "Вход не удался! Пожалуйста, проверьте свое имя пользователя и пароль."



@app.route('/dashboardAdmin', methods=['GET'])
def dashboardAdmin():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    generated_password = secrets.token_urlsafe(12)
    admin_generated_password = secrets.token_urlsafe(12)

    # Получаем результаты поиска из сессии
    searched_requests = session.get('searched_requests')
    searched_admins = session.get('searched_admins')

    # Если результаты поиска есть в сессии, используем их
    if searched_requests is not None:
        user_requests = searched_requests
    else:
        # Иначе загружаем все заявки из базы данных
        user_requests = list(mongo.db.requests.find({}))

    if searched_admins is not None:
        admins = searched_admins
    else:
        # Иначе загружаем всех администраторов из базы данных
        admins = list(mongo.db[ADMINS].find({}))

    return render_template('dashboardAdmin.html',
                           username=username,
                           user_requests=user_requests,
                           admins=admins,
                           generated_password=generated_password,
                           admin_generated_password=admin_generated_password,
                           search_query=session.get('searched_search_query'))
@app.route('/search_requests', methods=['POST'])
def search_requests():
    search_query_string = request.form.get('search_query', '')
    regex = re.compile(search_query_string, re.IGNORECASE)
    results = list(mongo.db.requests.find({'last_name': {'$regex': regex}}))
    print(results)
    # Преобразуем ObjectId в строки для сохранения в сессию
    for result in results:
        result['_id'] = str(result['_id'])

    # Сохраняем результаты поиска в сессию
    session['searched_requests'] = results
    session['searched_search_query'] =request.form.get('search_query', '')
    return redirect(url_for('dashboardAdmin'))


@app.route('/add_request/<arg1>', methods=['POST'])
def add_request(arg1):
    if request.method == 'POST':


        user = mongo.db[ADMINS].find_one({'admin_login': session.get('username')})
        # Формирование данных для добавления
        user_data = {
            'request_number': request.form['request_number'],
            'last_name': request.form['last_name'],
            'first_name': request.form['first_name'],
            'middle_name': request.form['middle_name'],
            'phone': request.form['phone'],
            'ssid': request.form['ssid'],
            'login': request.form['login'],
            'password': request.form['password'],
            'message': f"Ваш персональный пароль для подключения к сети {request.form['ssid']} : {arg1}",
            'adminInitials': f"{user.get('admin_last_name')} {user.get('admin_first_name')} {user.get('admin_middle_name')}"

        }

            # Добавление заявки в базу данных
        mongo.db.requests.insert_one(user_data)
        return redirect(url_for('dashboardAdmin'))


@app.route('/add_admin/<arg1>', methods=['POST'])
def add_admin(arg1):
    if request.method == 'POST':
        if 'admin_last_name' in request.form:
            # Проверка на пустоту полей
            required_fields = ['admin_last_name', 'admin_first_name', 'admin_middle_name', 'admin_type', 'admin_login', 'admin_password']
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'Поле {field} не должно быть пустым', 'danger')
                    return redirect(url_for('dashboardAdmin'))


            admin_data = {
                'admin_last_name': request.form['admin_last_name'],
                'admin_first_name': request.form['admin_first_name'],
                'admin_middle_name': request.form['admin_middle_name'],
                'admin_type': request.form['admin_type'],
                'admin_login': request.form['admin_login'],
                'admin_password': request.form['admin_password']
            }

            # Добавление администратора в базу данных
            mongo.db[ADMINS].insert_one(admin_data)
            admins = list(mongo.db[ADMINS].find())
            flash('Администратор успешно добавлен', 'success')
        return redirect(url_for('dashboardAdmin'))


@app.route('/delete_admins', methods=['POST'])
def delete_admins():
    try:
        selected_admins = request.form.getlist('selected_admins')
        print("Selected Admins:", selected_admins)

        # Найти текущего администратора
        current_admin = mongo.db[ADMINS].find_one({'admin_login': session.get('username')})
        current_admin_id = str(current_admin['_id'])
        print("Current Admin ID:", current_admin_id)

        # Удалить текущего администратора из списка для удаления, если он есть
        if current_admin_id in selected_admins:
            selected_admins.remove(current_admin_id)
            print("Selected Admins after removing current admin:", selected_admins)

        # Проверка и преобразование идентификаторов в ObjectId
        valid_object_ids = [ObjectId(admin_id) for admin_id in selected_admins if ObjectId.is_valid(admin_id)]
        print("Valid ObjectIds:", valid_object_ids)

        if valid_object_ids:
            mongo.db[ADMINS].delete_many({'_id': {'$in': valid_object_ids}})

        return redirect(url_for('dashboardAdmin'))

    except Exception as e:
        print(f"Error while deleting admins: {e}")
        return redirect(url_for('dashboardAdmin'))

@app.route('/delete_requests', methods=['POST'])
def delete_requests():
    try:
        session.pop('searched_requests', None)
        session.pop('searched_search_query', None)
        selected_requests = request.form.getlist('selected_requests')
        print("Selected Requests:", selected_requests)

        # Проверка и преобразование идентификаторов в ObjectId
        valid_object_ids = [ObjectId(req_id) for req_id in selected_requests if ObjectId.is_valid(req_id)]
        print("Valid ObjectIds:", valid_object_ids)

        if valid_object_ids:
            mongo.db.requests.delete_many({'_id': {'$in': valid_object_ids}})
        return redirect(url_for('dashboardAdmin'))

    except Exception as e:
        print(f"Error while deleting requests: {e}")
        return redirect(url_for('dashboardAdmin'))

if __name__ == '__main__':
    app.run()
