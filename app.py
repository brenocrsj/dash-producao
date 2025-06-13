# app.py
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask_login import LoginManager
import database
from logic.data_processing import load_and_prepare_data
from config import SECRET_KEY # Importa SECRET_KEY do seu arquivo config.py

def create_app():
    server = Flask(__name__)
    server.config.update(SECRET_KEY=SECRET_KEY)
    
    with server.app_context():
        database.init_db()

    app = Dash(__name__, server=server,
               external_stylesheets=[
                   dbc.themes.BOOTSTRAP,
                   dbc.icons.BOOTSTRAP,
                   '/assets/style.css' # Seu stylesheet personalizado
               ],
               suppress_callback_exceptions=True)
    app.title = "FleetMaster"
    
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        # Esta função carrega um usuário do banco de dados pelo ID
        # database.get_user_by_id já retorna uma instância da classe User (do database.py)
        return database.get_user_by_id(user_id)

    from components.layout import create_main_layout
    from logic.callbacks import register_callbacks

    df = load_and_prepare_data()
    app.layout = create_main_layout(df)
    register_callbacks(app, df)
    
    return app, server

# database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# ÚNICA DEFINIÇÃO DA CLASSE USER
class User(UserMixin):
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin # Adiciona o atributo is_admin

    # Métodos necessários pelo UserMixin
    def get_id(self):
        return str(self.id)

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
        
        # Verifica se a coluna is_admin já existe, e a adiciona se não existir (para bancos de dados existentes)
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
    with get_db_connection() as conn:
        # Seleciona todas as colunas, incluindo is_admin
        user_row = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user_row:
            # Instancia o objeto User passando todos os dados, incluindo is_admin
            # sqlite3.Row permite user_row['is_admin']
            return User(id=user_row['id'],
                        username=user_row['username'],
                        password_hash=user_row['password_hash'],
                        is_admin=bool(user_row['is_admin'])) # Converte 0/1 para True/False
    return None

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        # Seleciona todas as colunas, incluindo is_admin
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (int(user_id),)).fetchone()
        if user_row:
            # Instancia o objeto User passando todos os dados, incluindo is_admin
            return User(id=user_row['id'],
                        username=user_row['username'],
                        password_hash=user_row['password_hash'],
                        is_admin=bool(user_row['is_admin'])) # Converte 0/1 para True/False
    return None

def check_password(user_password_hash, password):
    return check_password_hash(user_password_hash, password)

# logic/callbacks.py
from dash import Input, Output, State, html, dcc, exceptions
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO
from flask_login import login_user, logout_user, current_user
from urllib.parse import parse_qs

import database
from components.sidebar import SIDEBAR_NAV_ITEMS
from components.tabs.analysis_tab import create_analysis_tab_layout, create_page_header
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout
from components.tabs.user_management_tab import create_user_management_layout


def register_callbacks(app, df):

    @app.callback(
        Output('login-wrapper', 'style'),
        Output('dashboard-wrapper', 'style'),
        Output('login-status-store', 'data'),
        Input('url', 'pathname')
    )
    def master_visibility_router(pathname):
        if current_user.is_authenticated:
            return {'display': 'none'}, {'display': 'block'}, {'is_authenticated': True, 'is_admin': current_user.is_admin, 'username': current_user.username}
        return {'display': 'flex'}, {'display': 'none'}, {'is_authenticated': False, 'is_admin': False, 'username': None}


    @app.callback(
        Output('page-content-container', 'children'),
        Output('page-title', 'children'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content_and_title(pathname, jsonified_data):
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate

        if jsonified_data:
            dff = pd.read_json(StringIO(jsonified_data), orient='split')
        else:
            dff = df.copy()
        
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div()
        page_title = "Página não encontrada"
        
        if pathname == "/":
            page_content, page_title = create_analysis_tab_layout(dff, 'dark'), "Análise Geral"
        elif pathname == "/matrix":
            page_content, page_title = create_matrix_tab_layout(dff, 'dark'), "Análise Matricial"
        elif pathname == "/efficiency":
            page_content, page_title = create_efficiency_tab_layout(dff, 'dark'), "Análise de Eficiência"
        elif pathname == "/management/users":
            if not current_user.is_admin:
                return dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4"), "Acesso Negado"
            page_content, page_title = create_user_management_layout(), "Gestão de Usuários"
        elif pathname in ["/management/equipment", "/settings"]:
            page_title = next(
                (item["title"] for item in SIDEBAR_NAV_ITEMS if item["href"] == pathname),
                "Página"
            )
            page_content = html.Div([
                create_page_header(page_title, "Funcionalidade em desenvolvimento."),
                dbc.Alert("Em breve.", color="info", className="m-4")
            ])
        elif pathname == "/logout":
            logout_user()
            return dcc.Location(pathname="/login", id="redirect-logout"), "Saindo..."
        else:
            page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        
        return page_content, page_title


    @app.callback(
        Output('url', 'pathname'),
        Output('login-output', 'children'),
        Input('login-button', 'n_clicks'),
        State('username-input', 'value'),
        State('password-input', 'value'),
        State('remember-me-checkbox', 'value'),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password, remember_me_value):
        if not username or not password:
            return exceptions.no_update, dbc.Alert("Preencha todos os campos.", color="warning", duration=3000)

        user = database.get_user_by_username(username)
        remember = 1 in remember_me_value 

        if user and database.check_password(user.password_hash, password):
            login_user(user, remember=remember)
            return "/", ""
        
        return exceptions.no_update, dbc.Alert("Nome de usuário ou senha inválidos.", color="danger", duration=3000)


    @app.callback(
        Output('user-management-message', 'children'),
        Input('create-user-button', 'n_clicks'),
        State('new-username-input', 'value'),
        State('new-password-input', 'value'),
        prevent_initial_call=True
    )
    def handle_internal_registration(n_clicks, username, password):
        if not username or not password: return dbc.Alert("Nome de usuário e senha são obrigatórios.", color="warning", duration=4000)
        if database.add_user(username, password): return dbc.Alert(f"Usuário '{username}' criado com sucesso!", color="success", duration=4000)
        return dbc.Alert(f"O nome de usuário '{username}' já existe.", color="danger", duration=4000)


    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('empresa-dropdown', 'value'),
        Input('destino-dropdown', 'value'),
        Input('material-dropdown', 'value')
    )
    def update_filtered_data(start_date, end_date, empresas, destinos, materiais):
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate

        dff = df.copy()
        
        if start_date and end_date:
            dff = dff[
                (dff['Data_Apenas'] >= pd.to_datetime(start_date).date()) &
                (dff['Data_Apenas'] <= pd.to_datetime(end_date).date())
            ]
        
        if empresas:
            dff = dff[dff['Empresa'].isin(empresas)]
        
        if destinos:
            dff = dff[dff['Destino'].isin(destinos)]
        
        if materiais:
            dff = dff[dff['Material'].isin(materiais)]
        
        return dff.to_json(date_format='iso', orient='split')


    @app.callback(
        Output('filtered-data-store', 'data', allow_duplicate=True),
        Output('date-picker-range', 'start_date'),
        Output('date-picker-range', 'end_date'),
        Output('empresa-dropdown', 'value'),
        Output('destino-dropdown', 'value'),
        Output('material-dropdown', 'value'),
        Input('clear-filters-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_all_filters(n_clicks):
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        
        return df.to_json(date_format='iso', orient='split'), \
               start_date, end_date, \
               [], [], []

    @app.callback(
        Output('dashboard-wrapper', 'className'),
        Output('sidebar-toggle-button', 'children'),
        Input('sidebar-toggle-button', 'n_clicks'),
        State('dashboard-wrapper', 'className'),
        prevent_initial_call=True
    )
    def toggle_sidebar(n_clicks, current_dashboard_class):
        if n_clicks is None:
            raise exceptions.PreventUpdate

        if 'sidebar-minimized' in current_dashboard_class:
            new_class = current_dashboard_class.replace(' sidebar-minimized', '')
            button_icon = html.I(className="bi bi-list", style={"font-size": "1.5rem"})
        else:
            new_class = current_dashboard_class + ' sidebar-minimized'
            button_icon = html.I(className="bi bi-x-lg", style={"font-size": "1.5rem"})

        return new_class, button_icon

    @app.callback(
        Output('nav-link-user-management', 'style'),
        Output('sidebar-user-info', 'children'),
        Output('header-user-name', 'children'),
        Input('login-status-store', 'data'),
    )
    def update_user_management_link_and_info_and_header(login_status):
        if login_status and login_status.get('is_authenticated'):
            username = login_status.get('username', 'Usuário')
            
            user_display_html = html.Div(
                html.Span(
                    username.capitalize(),
                    className="d-none d-md-inline-block me-2"
                )
            )

            if login_status.get('is_admin'):
                return {'display': 'flex'}, user_display_html, user_display_html
            else:
                return {'display': 'none'}, user_display_html, user_display_html
        else:
            return {'display': 'none'}, "Não logado", ""

# config.py
THEME_COLORS = {
    'dark': {
        'foreground': 'hsl(220, 15%, 90%)', 'primary': 'hsl(210, 85%, 65%)',
        'accent': 'hsl(38, 92%, 60%)', 'chart_1': 'hsl(210, 85%, 65%)',
        'chart_2': 'hsl(38, 92%, 60%)', 'chart_3': 'hsl(140, 70%, 55%)',
        'chart_4': 'hsl(260, 70%, 75%)', 'chart_5': 'hsl(190, 70%, 60%)',
    }
}

SECRET_KEY = 'sua_chave_secreta_aqui_para_seguranca_da_sessao'