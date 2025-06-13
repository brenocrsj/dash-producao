# database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# ÚNICA DEFINIÇÃO DA CLASSE USER (mover esta para cá se houver outra em app.py)
class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin # Adiciona o atributo is_admin

    # Métodos necessários pelo UserMixin
    def get_id(self):
        return str(self.id)

    # Você pode adicionar estas propriedades se precisar, mas não são estritamente necessárias pelo Flask-Login
    # @property
    # def is_active(self):
    #     return True

    # @property
    # def is_anonymous(self):
    #     return False

    # @property
    # def is_authenticated(self):
    #     return True # Já é tratado pelo Flask-Login se o objeto User existir

def get_db_connection():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

def init_db():
    with get_db_connection() as conn:
        # Cria a tabela users com a nova coluna is_admin (valor padrão 0 = False)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0 -- 0 para False, 1 para True
            );
        ''')
        
        # Verifica se a coluna is_admin já existe para evitar erro de ADD COLUMN em runs futuras
        cursor = conn.execute("PRAGMA table_info(users);")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_admin' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;')

        # Verifica e cria o usuário admin padrão 'breno@123' se ele não existir
        admin_user = conn.execute('SELECT id FROM users WHERE username = ?', ('breno@123',)).fetchone()
        if not admin_user:
            print("CRIANDO USUÁRIO ADMIN PADRÃO: breno@123")
            password_hash = generate_password_hash('breno@123')
            # Insere o usuário admin com is_admin = 1
            conn.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)', ('breno@123', password_hash, 1))
        conn.commit()

def add_user(username, password, is_admin=False): # Adiciona parâmetro is_admin
    with get_db_connection() as conn:
        try:
            # Insere o novo usuário, respeitando o status is_admin
            conn.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), 1 if is_admin else 0))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Usuário já existe
            return False

def get_user_by_username(username):
    print(f"DEBUG DB: Buscando usuário por username: {username}")
    with get_db_connection() as conn:
        user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user_row:
            print(f"DEBUG DB: Usuário '{username}' encontrado no DB. ID: {user_row['id']}, Admin: {bool(user_row['is_admin'])}")
            return User(id=user_row['id'],
                        username=user_row['username'],
                        password_hash=user_row['password_hash'],
                        is_admin=bool(user_row['is_admin']))
        print(f"DEBUG DB: Usuário '{username}' NÃO encontrado no DB.")
    return None

def get_user_by_id(user_id):
    print(f"DEBUG DB: Buscando usuário por ID: {user_id}")
    with get_db_connection() as conn:
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (int(user_id),)).fetchone()
        if user_row:
            print(f"DEBUG DB: Usuário com ID '{user_id}' encontrado. Username: {user_row['username']}")
            return User(id=user_row['id'],
                        username=user_row['username'],
                        password_hash=user_row['password_hash'],
                        is_admin=bool(user_row['is_admin']))
        print(f"DEBUG DB: Usuário com ID '{user_id}' NÃO encontrado.")
    return None

def check_password(user_password_hash, password):
    # Não printar a senha em texto claro, apenas o hash (primeiros 10 chars)
    print(f"DEBUG DB: Verificando senha. Hash DB: {user_password_hash[:10]}..., Senha input: {'*' * len(str(password))}")
    result = check_password_hash(user_password_hash, password)
    print(f"DEBUG DB: Resultado da verificação de senha: {result}")
    return result