# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_session import Session
from rasa_sdk.events import SlotSet
import mysql.connector

app = Flask(__name__)

app.secret_key = '8fcf2c518931e9f90ee4903350967dc4'


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Krunal2810",
        database="chatbot_data",
        auth_plugin='mysql_native_password'
    )


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/get_username', methods=['GET'])
# def get_username():
#     username = session.get('username', ' ')
#     SlotSet("username", username)
#     # return jsonify(username=username)
#     return f"username: {username}"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            SlotSet("username", username)

            # flash('Login successful', 'success')
            return redirect('/chatbot')
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        cursor.execute('SELECT * FROM users WHERE username = %s', (email,))
        existing_username = cursor.fetchone()

        if existing_user:
            flash('Email already exists. Please use another email for signup or login.', 'error')
            return render_template('signup.html')
        elif existing_username:
            flash('Username already exists. Please use another username', 'error')
            return render_template('signup.html')
        else:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()
            conn.close()
            # flash('User created successfully', 'success')
            return redirect('/login')

    return render_template('signup.html')


@app.route('/chatbot')
def open_chatbot():
    if 'username' not in session:
        return redirect('/login')
    username = session['username']
    print(username)
    return render_template('chatbot.html')


@app.route('/logout')
def logout():
    session['username'] = None
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

