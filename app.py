# app.py
from flask import Flask
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from flask_login import LoginManager
import database
from logic.data_processing import load_and_prepare_data
from config import SECRET_KEY

# Renomeada a função para evitar conflito com a variável global 'app'
def create_app_instance():
    flask_server = Flask(__name__)
    flask_server.config.update(SECRET_KEY=SECRET_KEY)
    
    with flask_server.app_context():
        database.init_db()

    dash_app = Dash(__name__, server=flask_server,
                   external_stylesheets=[
                       dbc.themes.BOOTSTRAP,
                       dbc.icons.BOOTSTRAP,
                       '/assets/style.css'
                   ],
                   suppress_callback_exceptions=True)
    dash_app.title = "FleetMaster"
    
    login_manager = LoginManager()
    login_manager.init_app(flask_server)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(user_id):
        return database.get_user_by_id(user_id)

    from components.layout import create_main_layout
    from logic.callbacks import register_callbacks

    df = load_and_prepare_data()
    dash_app.layout = create_main_layout(df)
    register_callbacks(dash_app, df)
    
    return dash_app, flask_server

# NOVO: Atribua explicitamente 'app' e 'server' globalmente chamando a função.
# O Gunicorn procurará por 'app' e 'server' neste nível.
app, server = create_app_instance()

# O bloco if __name__ == '__main__': (para rodar localmente com `python app.py`)
# pode ser mantido se você o tiver em um arquivo `run.py` separado, como parece ser o caso.
# Se você rodar `python app.py` diretamente, precisaria adicionar:
# if __name__ == '__main__':
#    app.run_server(debug=True)