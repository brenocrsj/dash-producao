# components/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from .auth_layout import create_auth_layout
from .header import create_header
from .filter_panel import create_filter_panel

def create_main_layout(df_full):
    """Cria o layout base COMPLETO da aplicação, com ambas as visualizações."""
    
    # Wrapper para a tela de autenticação
    login_layout = html.Div(
        create_auth_layout(),
        id='login-wrapper',
        className="login-container-wrapper"
    )

    # Wrapper para o dashboard principal
    # sidebar = create_sidebar() # REMOVIDO: A sidebar não será mais usada como elemento lateral
    header = create_header() # Este será a nova barra superior

    page_content_container = html.Div(id="page-content-container")
    
    main_content_area = dbc.Container([
        dbc.Row([
            dbc.Col(
                create_filter_panel(df_full),
                width=12, # Ocupa a largura total para o painel de filtros
                className="mb-4"
            )
        ]),
        dbc.Row([
            dbc.Col(
                page_content_container,
                width=12 # Ocupa a largura total para o conteúdo da página
            )
        ])
    ], fluid=True, className="page-content py-4")

    dashboard_layout = html.Div([
        header, # O header agora está no topo
        html.Main([main_content_area], className="content-below-topbar") # Nova classe para o conteúdo abaixo da barra superior
    ], 
    id='dashboard-wrapper',
    className="app-shell-topbar dark dashboard-container-wrapper", # Nova classe para o app shell com topbar
    )

    # Layout final contém os dcc.Store e os dois wrappers
    return html.Div([
        dcc.Location(id="url", refresh=True),
        dcc.Store(id='filtered-data-store'),
        dcc.Store(id='login-status-store'),
        login_layout,
        dashboard_layout
    ], style={'position': 'relative', 'height': '100vh', 'width': '100vw', 'overflow': 'hidden'})
def create_error_layout(error_message):
    """Cria uma página de erro para ser exibida quando os dados não podem ser carregados."""
    return html.Div(
        className="d-flex justify-content-center align-items-center vh-100", # Usa 100% da altura da viewport
        style={'backgroundColor': '#f8f9fa'}, # Um fundo cinza claro
        children=[
            dbc.Alert(
                [
                    html.H4("Erro Crítico na Aplicação", className="alert-heading"),
                    html.P(
                        "Não foi possível carregar os dados necessários para iniciar o dashboard. "
                        "Verifique a conexão de rede ou a fonte dos dados."
                    ),
                    html.Hr(),
                    html.P(f"Detalhe técnico do erro: {error_message}", className="mb-0 small"),
                ],
                color="danger",
                className="w-75 text-center" # Ocupa 75% da largura
            )
        ]
    )