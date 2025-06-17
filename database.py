# database.py
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor # <<< CORRIGIDO AQUI: DEVE SER DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env

# Configurações do Banco de Dados PostgreSQL (lendo do .env)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

# --- Modelagem de Usuário para Flask-Login ---
class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

# --- Funções de Conexão ao DB ---
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"ERRO DE CONEXÃO COM O BANCO DE DADOS: {e}")
        raise

def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Tabela de Usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE
                );
            ''')
            # Tabela de Clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    client_name VARCHAR(255) NOT NULL,
                    destination VARCHAR(255) UNIQUE NOT NULL
                );
            ''')
            # Tabela de Precificação
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pricing (
                    id SERIAL PRIMARY KEY,
                    destination VARCHAR(255) NOT NULL,
                    price_per_ton REAL NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    UNIQUE(destination, start_date, end_date)
                );
            ''')
            conn.commit()

            # Adiciona um usuário admin padrão se não existir
            cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING;",
                           ('admin', generate_password_hash('admin123'), True))
            conn.commit()
            print("Usuário 'admin' padrão criado (ou já existia).")

# --- Funções de Usuário ---
def add_user(username, password, is_admin=False):
    password_hash = generate_password_hash(password)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)",
                               (username, password_hash, is_admin))
                conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                return False
            except Exception as e:
                print(f"Erro ao adicionar usuário: {e}")
                conn.rollback()
                return False

def get_user_by_username(username):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['username'], user_data['password_hash'], user_data['is_admin'])
            return None

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data['id'], user_data['username'], user_data['password_hash'], user_data['is_admin'])
            return None

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

# --- Funções de Cliente ---
def add_client(client_name, destination):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO clients (client_name, destination) VALUES (%s, %s)",
                               (client_name, destination))
                conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                return False
            except Exception as e:
                print(f"Erro ao adicionar cliente: {e}")
                conn.rollback()
                return False

def get_all_clients():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            cursor.execute("SELECT * FROM clients ORDER BY client_name")
            return cursor.fetchall()

def get_client_by_destination(destination):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            cursor.execute("SELECT * FROM clients WHERE destination = %s", (destination,))
            return cursor.fetchone()

def update_client(client_id, new_client_name, new_destination):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT id FROM clients WHERE destination = %s AND id != %s", (new_destination, client_id))
                existing_client_with_new_destination = cursor.fetchone()
                if existing_client_with_new_destination:
                    print(f"Erro: Destino '{new_destination}' já está vinculado a outro cliente.")
                    return False

                cursor.execute("UPDATE clients SET client_name = %s, destination = %s WHERE id = %s",
                               (new_client_name, new_destination, client_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"Erro ao atualizar cliente {client_id}: {e}")
                conn.rollback()
                return False

def delete_client(client_id):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Erro ao deletar cliente {client_id}: {e}")
                conn.rollback()
                return False

# --- Funções de Precificação ---
def add_pricing(destination, price_per_ton, start_date_str, end_date_str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            try:
                new_start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                new_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

                if new_start_date > new_end_date:
                    print(f"Erro: Data de início ({start_date_str}) não pode ser posterior à data de fim ({end_date_str}).")
                    return False

                cursor.execute('''
                    SELECT start_date, end_date FROM pricing
                    WHERE destination = %s
                    AND ( (start_date <= %s) AND (end_date >= %s) )
                ''', (destination, end_date_str, start_date_str))
                
                existing_overlaps = cursor.fetchall()

                if existing_overlaps:
                    print(f"Erro: Período de {start_date_str} a {end_date_str} se sobrepõe a um período existente para o destino {destination}.")
                    return False

                cursor.execute("INSERT INTO pricing (destination, price_per_ton, start_date, end_date) VALUES (%s, %s, %s, %s)",
                               (destination, price_per_ton, new_start_date, new_end_date))
                conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                print(f"Erro de integridade ao adicionar precificação para {destination}: combinação já existe ou outro problema.")
                return False
            except Exception as e:
                conn.rollback()
                print(f"Erro inesperado ao adicionar precificação: {e}")
                return False

def get_all_pricing():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            cursor.execute("SELECT * FROM pricing ORDER BY destination, start_date")
            return cursor.fetchall()

def get_price_for_date(destination, target_date_obj):
    target_date_str = target_date_obj.strftime('%Y-%m-%d')
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor: # <<< CORRIGIDO AQUI
            price_data = cursor.execute('''
                SELECT price_per_ton FROM pricing
                WHERE destination = %s
                AND start_date <= %s
                AND end_date >= %s
                ORDER BY start_date DESC LIMIT 1
            ''', (destination, target_date_str, target_date_str)).fetchone()
            
            if price_data:
                return price_data['price_per_ton']
            return None

# Para testar (opcional)
if __name__ == '__main__':
    load_dotenv()
    try:
        conn_test = get_db_connection()
        if conn_test:
            print("Conexão com o PostgreSQL no Render bem-sucedida!")
            conn_test.close()
        else:
            print("Falha na conexão com o PostgreSQL.")
    except Exception as e:
        print(f"Erro durante o teste de conexão inicial: {e}")