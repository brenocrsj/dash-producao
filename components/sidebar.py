import dash_bootstrap_components as dbc
from dash import html, dcc

# --- NOVA FUNÇÃO PARA CRIAR O LAYOUT DO DASHBOARD ---
def create_dashboard_layout():
    # ITENS DA BARRA LATERAL (SIDEBAR)
    sidebar = html.Aside(className="sidebar", children=[
        html.Div(className="sidebar-header", children=[
            # Coloque sua logo aqui
            html.Img(src="/assets/logo.png", className="sidebar-logo"),
            html.H5("Seu Projeto", className="sidebar-title")
        ]),
        html.Hr(className="sidebar-divider"),
        # Links de navegação
        dbc.Nav(
            [
                dbc.NavLink([html.I(className="bi bi-house-door-fill me-2"), "Home"], href="/main/home", active="exact"),
                dbc.NavLink([html.I(className="bi bi-bar-chart-fill me-2"), "Análises"], href="/main/analises", active="exact"),
                dbc.NavLink([html.I(className="bi bi-table me-2"), "Relatórios"], href="/main/relatorios", active="exact"),
                dbc.NavLink([html.I(className="bi bi-gear-fill me-2"), "Configurações"], href="/main/configuracoes", active="exact"),
            ],
            vertical=True,
            pills=True,
            className="sidebar-nav"
        )
    ])

    # ÁREA DE CONTEÚDO PRINCIPAL
    main_content_area = html.Div(className="main-content-area", children=[
        # Cabeçalho Superior
        html.Header(className="top-header", children=[
            # Você pode adicionar breadcrumbs, busca ou outros itens aqui
            html.P("Dashboard / Home", className="breadcrumb-text"),
            # Exemplo de avatar do usuário
            html.Div(className="user-profile", children=[
                html.Img(src="https://via.placeholder.com/40", className="user-avatar"),
                "Usuário Admin"
            ])
        ]),
        # Onde o conteúdo das suas páginas será renderizado
        html.Main(className="page-content", id="page-content")
    ])

    # Layout final que combina a sidebar e a área de conteúdo
    return html.Div(className="app-shell-sidebar", children=[sidebar, main_content_area])
