# components/header.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user

# Copie e cole os itens de navegação aqui, vindos de components/sidebar.py
TOPBAR_NAV_ITEMS = [
    {"icon": "bi bi-graph-up", "label": "Análise Geral", "href": "/"},
    {"icon": "bi bi-grid-3x3-gap-fill", "label": "Análise Matricial", "href": "/matrix"},
    {"icon": "bi bi-speedometer", "label": "Análise de Eficiência", "href": "/efficiency"},
    {"icon": "bi bi-people", "label": "Gestão de Usuários", "href": "/management/users", "id": "nav-link-user-management"},
    {"icon": "bi bi-tools", "label": "Gestão de Equipamentos", "href": "/management/equipment"},
    {"icon": "bi bi-gear", "label": "Configurações", "href": "/settings"},
]

def create_header():
    user_name_display = html.Div(id="header-user-name")

    # Cria os links de navegação para a barra superior
    nav_links = []
    for item in TOPBAR_NAV_ITEMS:
        nav_link_args = {
            "children": [
                # CORRIGIDO: Combinado os dois className em um só, separados por espaço
                html.I(className=f"{item['icon']} me-2"), # Ícone com margem à direita
                item["label"] # Apenas o texto do label
            ],
            "href": item["href"],
            "active": "exact",
            "className": "nav-link px-3 py-2" # Estilos de link Bootstrap: padding horizontal e vertical
        }
        if "id" in item:
            nav_link_args["id"] = item["id"]
        
        nav_links.append(
            html.Li(
                dbc.NavLink(**nav_link_args),
                className="nav-item" # Item de navegação Bootstrap
            )
        )

    return html.Header(
        className="topbar-header", # Nova classe para o cabeçalho superior
        children=[
            # Logo ou Título da Aplicação
            html.A(
                href="/",
                className="navbar-brand-custom", # Nova classe para a marca/logo
                children=[
                    html.I(className="bi bi-command me-2", style={"font-size": "1.8rem", "color": "hsl(var(--accent))"}),
                    html.Span("FleetMaster", className="app-brand-title")
                ]
            ),

            # Navegação principal (links)
            html.Nav(
                className="main-nav-links ms-auto", # Nova classe para os links, ms-auto para alinhar à direita
                children=[
                    html.Ul(
                        className="nav nav-pills d-flex", # Flex para alinhar horizontalmente
                        children=nav_links
                    )
                ]
            ),
            
            # Avatar do usuário com dropdown (mantido)
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label=html.Div([
                    user_name_display,
                    html.Div(
                        html.I(className="bi bi-person-circle", style={"font-size": "1.5rem"}),
                        className="avatar-button"
                    )
                ], className="d-flex align-items-center"),
                children=[
                    dbc.DropdownMenuItem("Perfil", href="/settings"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Sair", href="/logout", id="logout-link", className="text-danger"),
                ],
                align_end=True,
                toggle_style={"background": "none", "border": "none", "padding": "0"}
            ),
        ]
    )