# netlify/app/main.py
# Este arquivo é o ponto de entrada para a Netlify Function.

import sys
import os

# Adiciona a pasta raiz do projeto ao PATH para que o main.py possa importar app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Importa o app Dash do seu app.py original
# Assumimos que seu app.py define uma variável 'server' para o Gunicorn
from app import server as app_server

# Isso é necessário para usar o serverless-wsgi para empacotar a aplicação Flask/Dash
from serverless_wsgi import handle_request

def handler(event, context):
    # O serverless_wsgi.handle_request traduz a requisição da Lambda para o formato WSGI
    # e passa para o seu app_server (que é o app.server do seu Dash).
    # Ele também traduz a resposta do Dash de volta para o formato que a Lambda espera.
    return handle_request(app_server, event, context)