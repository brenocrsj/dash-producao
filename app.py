# app.py
from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager
import pandas as pd # Adicionado para o caso de o df falhar
import sys # Adicionado para o caso de o df falhar

# Importações dos seus módulos
import database
from logic.data_processing import load_and_prepare_data
from config import SECRET_KEY
from components.layout import create_main_layout, create_error_layout
from logic.callbacks import register_callbacks

# Função única para criar a instância da aplicação
def create_app_instance():
    """
    Cria e configura as instâncias do Flask e do Dash,
    incluindo tratamento de erros no carregamento de dados.
    """
    flask_server = Flask(__name__)
    flask_server.config.update(SECRET_KEY=SECRET_KEY)
    
    with flask_server.app_context():
        database.init_db()

    dash_app = Dash(__name__, server=flask_server,
                    external_stylesheets=[
                        dbc.themes.BOOTSTRAP,
                        dbc.icons.BOOTSTRAP,
                    ],
                    suppress_callback_exceptions=True)
    dash_app.title = "FleetMaster"
    
    # Configuração do Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(flask_server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        return database.get_user_by_id(user_id)
    
    try:
        # 1. Tenta carregar os dados
        df = load_and_prepare_data()

        # 2. Verificação crucial (opcional, mas recomendado)
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("A função load_and_prepare_data() retornou um DataFrame vazio ou inválido.")

        # 3. Se os dados forem carregados com sucesso, cria o layout principal
        print("Dados carregados com sucesso. Construindo layout principal...")
        dash_app.layout = create_main_layout(df)
        register_callbacks(dash_app, df)

    except Exception as e:
        # 4. Se ocorrer QUALQUER erro durante o carregamento, captura a exceção
        print(f"ERRO FATAL AO CARREGAR OS DADOS: {e}")
        
        # 5. Em vez de quebrar, exibe uma página de erro segura
        dash_app.layout = create_error_layout(str(e))
        # Callbacks não são registrados, pois não há dados para eles

    return dash_app, flask_server

app, server = create_app_instance()