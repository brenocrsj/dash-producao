import dash_bootstrap_components as dbc
from dash import html
# Importamos a função de cabeçalho do local correto
from .analysis_tab import create_page_header

def create_user_management_layout():
    """Cria o layout da página de gerenciamento de usuários."""
    
    form = dbc.Card([
        dbc.CardHeader(html.H4("Cadastrar Novo Usuário")),
        dbc.CardBody([
            html.Div(id="user-management-message"),
            
            dbc.Label("Nome do Novo Usuário:", html_for="new-username-input"),
            dbc.Input(id="new-username-input", placeholder="Ex: julia.silva", type="text", className="mb-3"),
            
            dbc.Label("Senha do Novo Usuário:", html_for="new-password-input"),
            dbc.Input(id="new-password-input", placeholder="********", type="password", className="mb-3"),
            
            dbc.Button("Criar Usuário", id="create-user-button", color="primary")
        ])
    ], className="content-card")

    layout = html.Div([
        create_page_header("Gestão de Usuários", "Crie e gerencie as contas de acesso ao sistema."),
        form
    ])

    return layout