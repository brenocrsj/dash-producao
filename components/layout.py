from dash import html, dcc
import dash_bootstrap_components as dbc
from .auth_layout import create_auth_layout
from .header import create_header
from .filter_panel import create_filter_panel

def create_main_layout(df_full):
    """Cria o layout base com a nova tela de carregamento de sobreposição."""
    
    login_layout = html.Div(create_auth_layout(), id='login-wrapper', className="login-container-wrapper")
    header = create_header()
    main_content_area = dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Div(id='filter-panel-wrapper', children=create_filter_panel(df_full)),
                md=3, id='filter-col', className="mb-4 d-flex justify-content-center align-items-start"
            ),
            dbc.Col(
                html.Div(id='page-content-container'), # O conteúdo real da página
                md=9, id='page-content-col'
            )
        ])
    ], fluid=True, className="page-content py-4")

    dashboard_layout = html.Div([
        header,
        html.Main([main_content_area], className="content-below-topbar")
    ], id='dashboard-wrapper', className="app-shell-topbar dark dashboard-container-wrapper")

    # <<< CORREÇÃO PRINCIPAL AQUI: Definindo a nova animação >>>
    custom_spinner = html.Div(
        className="loader-animation-container",  # O novo container da animação
        children=[
            # A "carga" (ícone de caixa que se move)
            html.I(className="bi bi-box-seam loader-load-item"),
            # O caminhão (que fica parado)
            html.I(className="bi bi-truck loader-truck-base")
        ]
    )

    # Layout final com o dcc.Loading global
    return html.Div([
        # O dcc.Loading agora usa o 'custom_spinner' que acabamos de criar
        dcc.Loading(
            id="loading-global",
            type="default",
            className="loading-overlay",
            children=custom_spinner # Passando a nova animação
        ),
        
        # O resto do seu layout original
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