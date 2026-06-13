from flask import Flask, render_template, request, redirect, url_for, session, abort
from datetime import timedelta
import sqlite3
import auth
import logs
import os
from dotenv import load_dotenv 


app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    raise ValueError('Файл .env не найден или в нем нет SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=3)
DB_PORTFOLIO = 'portfolio.db'

def init_portfolio_db():
    conn = sqlite3.connect(DB_PORTFOLIO)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            short_info TEXT,
            detailed_info TEXT,
            projects TEXT
        )
    ''')
    conn.commit()
    conn.close()

auth.init_auth_db()
logs.init_logs_db()
init_portfolio_db()

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PORTFOLIO)
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, short_info FROM portfolio')
    profiles = cursor.fetchall()
    conn.close()
    logs.log_action(session.get('user', 'Guest'), 'View Landing', 'Success')
    return render_template('index.html', profiles=profiles)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if auth.register_user(username, password):
            conn = sqlite3.connect(DB_PORTFOLIO)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO portfolio (username) VALUES (?)', (username,))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        else:
            return 'Ошибка регистрации. Возможно, пользователь уже существует'
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if auth.authenticate_user(username, password):
            session['user'] = username
            return redirect(url_for('edit_profile'))
        else:
            return 'Неверный логин или пароль'
    return render_template('login.html')

@app.route('/logout')
def logout():
    logs.log_action(session.get('user', 'Unknown'), 'Logout', 'Success')
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def view_profile(username):
    conn = sqlite3.connect(DB_PORTFOLIO)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM portfolio WHERE username = ?', (username,))
    profile = cursor.fetchone()
    conn.close()
    if not profile:
        abort(404)
    logs.log_action(session.get('user', 'Guest'), f'View Profile: {username}', 'Success')
    return render_template('profile.html', profile=profile)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'user' not in session:
        abort(403)
    username = session['user']
    if request.method == 'POST':
        full_name = request.form.get('full_name', '')
        short_info = request.form.get('short_info', '')
        detailed_info = request.form.get('detailed_info', '')
        projects = request.form.get('projects', '')
        conn = sqlite3.connect(DB_PORTFOLIO)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE portfolio 
            SET full_name=?, short_info=?, detailed_info=?, projects=? 
            WHERE username=?
        ''', (full_name, short_info, detailed_info, projects, username))
        conn.commit()
        conn.close()
        logs.log_action(username, 'Edit Profile', 'Success')
        return redirect(url_for('edit_profile'))

    conn = sqlite3.connect(DB_PORTFOLIO)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM portfolio WHERE username = ?', (username,))
    profile = cursor.fetchone()
    conn.close()
    logs.log_action(username, 'Open Edit Page', 'Success')
    return render_template('edit.html', profile=profile)

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
