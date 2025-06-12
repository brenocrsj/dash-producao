# components/sidebar.py

from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

# Definição dos itens da navegação em um formato fácil de gerenciar
# No futuro, podemos adicionar links para 'Análise Matricial', 'Gestão de Equipamentos', etc.
SIDEBAR_NAV_ITEMS = [
    {"title": "Análise Geral", "href": "/", "icon": "lucide:layout-dashboard"},
    {"title": "Análise Matricial", "href": "/matrix", "icon": "lucide:table-cells-merge"},
    {"title": "Análise de Eficiência", "href": "/efficiency", "icon": "lucide:line-chart"},
    {"title": "Gestão de Equipamentos", "href": "/management/equipment", "icon": "lucide:truck", "disabled": True},
    {"title": "Gestão de Usuários", "href": "/management/users", "icon": "lucide:users", "disabled": True},
    {"title": "Configurações", "href": "/settings", "icon": "lucide:settings", "disabled": True},
]

def create_sidebar():
    """
    Cria o componente da barra lateral de navegação.
    """
    
    # Cabeçalho da Sidebar
    sidebar_header = html.Div([
        dbc.NavLink(
            [
                DashIconify(icon="lucide:gauge", width=32, height=32, className="text-primary"),
                html.H1("FleetMaster", className="sidebar-title")
            ],
            href="/",
            active="exact",
            className="sidebar-header-link"
        )
    ], className="sidebar-header")

    # Menu com os links de navegação
    nav_menu = dbc.Nav(
        [
            dbc.NavLink(
                [
                    DashIconify(icon=item["icon"], width=20, height=20, className="me-3"),
                    html.Span(item["title"])
                ],
                href=item["href"],
                active="exact",
                disabled=item.get("disabled", False) # Pega o valor de 'disabled', ou False se não existir
            )
            for item in SIDEBAR_NAV_ITEMS
        ],
        vertical=True,
        pills=True,
        className="flex-grow-1"
    )
    
    # Rodapé da Sidebar
    sidebar_footer = html.Div([
        dbc.NavLink(
            [
                DashIconify(icon="lucide:log-out", width=20, height=20, className="me-3"),
                html.Span("Sair")
            ],
            href="/logout",
            active="exact"
        )
    ], className="sidebar-footer")

    # Montagem final da Sidebar
    sidebar = html.Div(
        [sidebar_header, nav_menu, sidebar_footer],
        className="sidebar"
    )

    return sidebar