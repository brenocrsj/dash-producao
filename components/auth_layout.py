# components/auth_layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_auth_layout():
    return html.Div(
        className="auth-container-background", # Classe para a imagem de fundo PNG
        children=[
            dbc.Card(
                [
                    # Seção da Logo (centralizada no topo do card)
                    dbc.CardHeader(
                        html.Div(
                            html.Img(src="/assets/logo_fleetmaster.png", className="login-logo"), # Substitua pelo caminho da sua logo PNG
                            className="login-logo-container"
                        )
                    ),
                    dbc.CardBody(
                        [
                            # REMOVIDO: html.H2("Login", className="card-title text-center mb-4 login-title"),
                            html.Div(className="mb-4"), # Espaçamento para compensar a remoção do título
                            
                            # Input de Usuário com Ícone
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(html.I(className="bi bi-person login-icon")),
                                    dbc.Input(
                                        id="username-input",
                                        type="text",
                                        placeholder="Nome de Usuário",
                                        className="login-input"
                                    ),
                                ],
                                className="mb-3"
                            ),
                            
                            # Input de Senha com Ícone
                            dbc.InputGroup(
                                [
                                    dbc.InputGroupText(html.I(className="bi bi-lock login-icon")),
                                    dbc.Input(
                                        id="password-input",
                                        type="password",
                                        placeholder="Senha",
                                        className="login-input"
                                    ),
                                ],
                                className="mb-3"
                            ),
                            
                            # Opção "Lembrar senha"
                            dbc.Checklist(
                                options=[{"label": "Lembrar senha", "value": 1}],
                                value=[],
                                id="remember-me-checkbox",
                                inline=True,
                                switch=True,
                                className="mb-4 login-remember-me"
                            ),
                            
                            # Botão de Login
                            dbc.Button(
                                "Entrar",
                                id="login-button",
                                color="primary",
                                className="w-100 mb-3 login-button"
                            ),
                            
                            html.Div(id="login-output", className="mt-3 text-center text-danger login-error-message"),
                        ]
                    )
                ],
                className="auth-card login-card-border"
            )
        ]
    )