# components/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from .auth_layout import create_auth_layout
from .header import create_header
from .filter_panel import create_filter_panel

def create_main_layout(df_full):
    """Cria o layout base COMPLETO da aplicação, com a tela de carregamento correta."""
    
    login_layout = html.Div(
        create_auth_layout(),
        id='login-wrapper',
        className="login-container-wrapper"
    )

    header = create_header()

    # --- Definindo o spinner personalizado para deixar o código mais limpo ---
    custom_spinner = html.Div(html.I(className="bi bi-truck loading-truck"))

    main_content_area = dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div(
                    id='filter-panel-wrapper',
                    children=create_filter_panel(df_full)
                ),
                md=3,
                id='filter-col',
                className="mb-4 d-flex justify-content-center align-items-start"
            ),
            
            # <<< A CORREÇÃO FINAL E DEFINITIVA ESTÁ NESTA COLUNA >>>
            dbc.Col(
                # Usamos dcc.Loading para envolver diretamente o conteúdo da página.
                dcc.Loading(
                    id="loading-content",
                    type="default", # Não mostra o spinner padrão
                    className="loading-overlay", # Aplica o fundo transparente do seu CSS
                    custom_spinner=custom_spinner, # <<< USANDO A PROPRIEDADE CORRETA
                    children=[
                        # O conteúdo que será carregado (e que o Loading vai "observar") vai aqui
                        html.Div(id='page-content-container')
                    ]
                ),
                md=9,
                id='page-content-col'
            )
        ])
    ], fluid=True, className="page-content py-4")

    dashboard_layout = html.Div([
        header,
        html.Main([main_content_area], className="content-below-topbar")
    ], 
    id='dashboard-wrapper',
    className="app-shell-topbar dark dashboard-container-wrapper",
    )

    # O resto do seu layout permanece o mesmo
    return html.Div([
        dcc.Location(id="url", refresh=True),
        dcc.Store(id='filtered-data-store'),
        dcc.Store(id='login-status-store'),
        dcc.Store(id='filter-toggle-store', data={'is_hidden': False}),
        login_layout,
        dashboard_layout
    ], style={'position': 'relative', 'height': '100vh', 'width': '100vw', 'overflow': 'hidden'})

def create_error_layout(error_message):
    """Cria uma página de erro para ser exibida quando os dados não podem ser carregados."""
    return html.Div(
        className="d-flex justify-content-center align-items-center vh-100",
        style={'backgroundColor': '#f8f9fa'},
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
                className="w-75 text-center"
            )
        ]
    )