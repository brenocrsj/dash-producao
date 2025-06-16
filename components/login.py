# components/login.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from config import THEME_COLORS # Para usar cores no login

def create_login_layout(): # Removido 'theme' do parâmetro, obtém colors internamente
    """Cria o layout da página de autenticação (login)."""
    colors = THEME_COLORS['light'] # Usar o tema 'light' para o login

    return html.Div(
        className="auth-container-background",
        children=[
            dbc.Card(
                [
                    html.Div([
                        html.Img(src="/assets/logo_fleetmaster.png", className="login-logo"),
                    ], className="login-logo-container"),
                    
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(html.I(className="bi bi-person login-icon")),
                            dbc.Input(id="username", placeholder="Usuário", type="text", className="login-input"),
                        ],
                        className="mb-3",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(html.I(className="bi bi-lock login-icon")),
                            dbc.Input(id="password", placeholder="Senha", type="password", className="login-input"),
                        ],
                        className="mb-3",
                    ),
                    html.Div( # Substitui dbc.FormGroup
                        [
                            dbc.Checkbox(id="remember-me", label="Lembrar-me", className="form-check-input"),
                            html.Label("Lembrar-me", htmlFor="remember-me", className="form-check-label")
                        ],
                        className="login-remember-me mb-4"
                    ),
                    dbc.Button("Entrar", id="login-button", n_clicks=0, className="login-button w-100"),
                    html.Div(id="login-output", className="login-error-message mt-3"),
                ],
                className="auth-card"
            )
        ]
    )