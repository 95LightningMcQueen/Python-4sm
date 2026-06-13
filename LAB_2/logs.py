import sqlite3
from datetime import datetime


DB_LOGS = 'logs.db'

def init_logs_db():
    conn = sqlite3.connect(DB_LOGS)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Login TEXT,
            Date TEXT,
            Time TEXT,
            Action TEXT,
            Result TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_action(login, action, result):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    conn = sqlite3.connect(DB_LOGS)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (Login, Date, Time, Action, Result) 
        VALUES (?, ?, ?, ?, ?)
    ''', (login, date_str, time_str, action, result))
    conn.commit()
    conn.close()
