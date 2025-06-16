# components/login_page.py
from dash import html, dcc
import dash_bootstrap_components as dbc

# Esta é a função que seu app.py está tentando importar
def serve_layout():
    return dbc.Container([
        dbc.Row(dbc.Col(html.H2("Página de Login", className="text-center my-5"), width=12)),
        dbc.Row(dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.P("Conteúdo da tela de login aqui."),
                    dbc.Button("Entrar", color="primary", className="mt-3")
                ])
            ], className="shadow-sm"),
            width=6, lg=4, className="mx-auto" # Centraliza o card na página
        ))
    ], fluid=True, className="p-4")