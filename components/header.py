# components/header.py
from dash import html, dcc
import dash_bootstrap_components as dbc
# from flask_login import current_user # REMOVA esta importação (já removida nas etapas anteriores)

def create_header():
    # O nome do usuário será atualizado via callback, inicialmente vazio ou placeholder
    user_name_display = html.Div(id="header-user-name")

    return html.Header(
        className="site-header",
        children=[
            # Botão de toggle para a sidebar
            dbc.Button(
                html.I(className="bi bi-list", style={"font-size": "1.5rem"}), # Ícone de hamburguer
                id="sidebar-toggle-button",
                className="me-3", # Margem à direita
                color="light", # Cor clara para o botão
                outline=True, # Botão outline
                style={"border": "none"} # Remover borda para um visual mais limpo
            ),
            html.Div(id="page-title", className="flex-grow-1"), # Título da página (será preenchido via callback)
            
            # Avatar do usuário com dropdown
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                # O label do dropdown agora usa o html.Div com o ID para ser atualizado
                label=html.Div([
                    user_name_display, # Placeholder para o nome do usuário
                    html.Div(
                        html.I(className="bi bi-person-circle", style={"font-size": "1.5rem"}), # Ícone de usuário
                        className="avatar-button"
                    )
                ], className="d-flex align-items-center"),
                children=[
                    dbc.DropdownMenuItem("Perfil", href="/settings"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Sair", href="/logout", id="logout-link", className="text-danger"),
                ],
                align_end=True, # CORRIGIDO: Troquei align_right por align_end
                toggle_style={"background": "none", "border": "none", "padding": "0"} # Estilo para o toggle do dropdown
            ),
        ]
    )