# components/header.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user

# Itens de navegação para a barra superior
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

    # Cria os links de navegação para o Collapse (que será o menu mobile)
    nav_links_children = []
    for item in TOPBAR_NAV_ITEMS:
        nav_link_args = {
            "children": [
                html.I(className=f"{item['icon']} me-2"),
                item["label"]
            ],
            "href": item["href"],
            "active": "exact",
            "className": "nav-link px-3 py-2" # Estilos de link Bootstrap
        }
        if "id" in item:
            nav_link_args["id"] = item["id"]
        
        nav_links_children.append(dbc.NavLink(**nav_link_args))

    return dbc.Navbar(
        id="topbar-navbar", # ID para o Navbar
        class_name="topbar-header", # Reutiliza a classe para estilização de fundo/sombra
        children=[
            # Logo ou Título da Aplicação
            # CORRIGIDO: class_name -> className para html.A
            html.A(
                href="/",
                className="navbar-brand-custom", # Usar className
                children=[
                    html.I(className="bi bi-command me-2", style={"fontSize": "1.8rem", "color": "hsl(var(--accent))"}),
                    html.Span("FleetMaster", className="app-brand-title")
                ]
            ),

            # Botão de alternar (toggler) para o menu mobile
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0, class_name="ms-auto", children=html.I(className="bi bi-list")),

            # Conteúdo colapsável (links de navegação)
            dbc.Collapse(
                dbc.Nav(
                    nav_links_children,
                    class_name="ml-auto flex-column flex-md-row"
                ),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
                class_name="justify-content-end"
            ),
            
            # Avatar do usuário com dropdown (mantido, mas precisa ser um dbc.NavItem)
            dbc.Nav(
                class_name="ms-2",
                children=[
                    dbc.NavItem(
                        dbc.DropdownMenu(
                            nav=True,
                            in_navbar=True,
                            label=html.Div([
                                user_name_display,
                                html.Div(
                                    html.I(className="bi bi-person-circle", style={"fontSize": "1.5rem"}),
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
                        )
                    )
                ]
            )
        ],
        dark=True,
    )