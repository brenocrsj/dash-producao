# app.py
from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc
from flask_login import LoginManager
import database
from logic.data_processing import load_and_prepare_data

def create_app():
    server = Flask(__name__)
    server.config.update(SECRET_KEY='uma-chave-secreta-final-e-segura-e-aleatoria')
    
    with server.app_context():
        database.init_db()

    app = Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
    app.title = "FleetMaster"
    
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        return database.get_user_by_id(user_id)

    from components.layout import create_main_layout
    from logic.callbacks import register_callbacks

    df = load_and_prepare_data()
    app.layout = create_main_layout(df)
    register_callbacks(app, df)
    
    return app, server