# database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id; self.username = username; self.password_hash = password_hash

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False); conn.row_factory = sqlite3.Row; return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);')
        admin_user = conn.execute('SELECT id FROM users WHERE username = ?', ('breno@123',)).fetchone()
        if not admin_user:
            print("CRIANDO USUÁRIO ADMIN PADRÃO: breno@123")
            password_hash = generate_password_hash('breno@123')
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('breno@123', password_hash))
        conn.commit()

def add_user(username, password):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, generate_password_hash(password)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_user_by_username(username):
    with get_db_connection() as conn:
        user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user_row: return User(id=user_row['id'], username=user_row['username'], password_hash=user_row['password_hash'])
    return None

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (int(user_id),)).fetchone()
        if user_row: return User(id=user_row['id'], username=user_row['username'], password_hash=user_row['password_hash'])
    return None

def check_password(user_password_hash, password):
    return check_password_hash(user_password_hash, password)