# components/auth_layout.py

from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def create_auth_layout(form_type='login'):
    """Cria o layout para as telas de login ou cadastro."""
    
    if form_type == 'login':
        title = "Bem-vindo de volta!"
        description = "Faça login para acessar o dashboard."
        button_text = "Entrar"
        button_id = "login-button"
        switch_link_text = "Não tem uma conta? Cadastre-se"
        switch_link_href = "/register"
    else: # register
        title = "Crie sua Conta"
        description = "Preencha os campos para iniciar."
        button_text = "Cadastrar"
        button_id = "register-button"
        switch_link_text = "Já tem uma conta? Faça login"
        switch_link_href = "/login"

    return html.Div([
        html.Div([
            DashIconify(icon="lucide:gauge", width=48, className="mb-4 text-primary"),
            html.H1(title, className="h2"),
            html.P(description, className="text-muted"),
            
            # Div para exibir mensagens de erro
            html.Div(id="auth-message"),
            
            dbc.Input(id="username-input", placeholder="Usuário", type="text", className="mb-3"),
            dbc.Input(id="password-input", placeholder="Senha", type="password", className="mb-3"),
            
            dbc.Button(button_text, id=button_id, color="primary", className="w-100 mb-3"),
            
            dcc.Link(switch_link_text, href=switch_link_href, className="fs-sm")
            
        ], className="auth-card")
    ], className="auth-container")