import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import logs


DB_USERS = 'users.db'

def init_auth_db():
    conn = sqlite3.connect(DB_USERS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_USERS)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            logs.log_action(username, 'Registration', 'Failed: User exists')
            return False
        p_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, p_hash))
        conn.commit()
        logs.log_action(username, 'Registration', 'Success')
        return True
    except Exception as e:
        logs.log_action(username, 'Registration', f'Error: {str(e)}')
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_USERS)
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        logs.log_action(username, 'Login', 'Success')
        return True
    logs.log_action(username, 'Login', 'Failed: Wrong credentials')
    return False
