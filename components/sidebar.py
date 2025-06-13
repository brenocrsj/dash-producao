# components/sidebar.py
from dash import html, dcc
import dash_bootstrap_components as dbc
# from flask_login import current_user # REMOVA esta importação, não é mais necessária aqui para o layout inicial

SIDEBAR_NAV_ITEMS = [
    {"icon": "bi bi-graph-up", "label": "Análise Geral", "href": "/"},
    {"icon": "bi bi-grid-3x3-gap-fill", "label": "Análise Matricial", "href": "/matrix"},
    {"icon": "bi bi-speedometer", "label": "Análise de Eficiência", "href": "/efficiency"},
    {"icon": "bi bi-people", "label": "Gestão de Usuários", "href": "/management/users", "id": "nav-link-user-management"}, # Este tem um ID
    {"icon": "bi bi-tools", "label": "Gestão de Equipamentos", "href": "/management/equipment"},
    {"icon": "bi bi-gear", "label": "Configurações", "href": "/settings"},
]

def create_sidebar():
    # Cria os links de navegação da sidebar
    nav_links = []
    for item in SIDEBAR_NAV_ITEMS:
        # O link de gestão de usuários será sempre adicionado aqui.
        # A visibilidade será controlada por um callback posteriormente.
        
        # Dicionário para armazenar os argumentos do dbc.NavLink
        nav_link_args = {
            "children": [
                html.I(className=f"{item['icon']}"), # Ícone
                html.Span(item["label"], className="sidebar-nav-text") # Texto do link, com nova classe
            ],
            "href": item["href"],
            "active": "exact",
            "className": "nav-link" # Mantém a classe nav-link
        }
        
        # Adiciona a propriedade 'id' SOMENTE SE ela existir no dicionário do item
        if "id" in item:
            nav_link_args["id"] = item["id"]

        nav_links.append(
            html.Li(
                dbc.NavLink(**nav_link_args), # Desempacota o dicionário como argumentos nomeados
                className="nav-item sidebar-nav-item" # Adiciona nova classe para o item
            )
        )

    # placeholder para o nome de usuário no rodapé, será atualizado via callback
    user_info_display = html.Span(id="sidebar-user-info", className="text-muted small")

    return html.Nav(
        className="sidebar", # Classe inicial para a sidebar
        children=[
            html.Div(
                className="sidebar-header", # Classe para o cabeçalho da sidebar
                children=[
                    html.A(
                        href="/",
                        className="sidebar-header-link",
                        children=[
                            html.I(className="bi bi-command", style={"font-size": "2rem", "color": "hsl(var(--accent))"}), # Ícone de logo
                            html.Span("FleetMaster", className="sidebar-title") # Título da aplicação
                        ]
                    )
                ]
            ),
            html.Ul(
                className="nav nav-pills flex-column mb-auto", # Classes do Bootstrap para navegação
                children=nav_links
            ),
            html.Div(
                className="sidebar-footer", # Classe para o rodapé da sidebar
                children=[
                    html.Div(
                        className="user-info", # Nova classe para esconder o texto do usuário
                        children=[
                            user_info_display # Usa o placeholder
                        ]
                    )
                ]
            )
        ]
    )