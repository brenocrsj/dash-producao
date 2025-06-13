# components/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc # Importar DBC
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
    header = create_header()
    
    page_content_container = html.Div(id="page-content-container")
    
    main_content_area = dbc.Container([
        dbc.Row([
            dbc.Col(
                create_filter_panel(df_full),
                width=12,
                className="mb-4"
            )
        ]),
        dbc.Row([
            dbc.Col(
                page_content_container,
                width=12
            )
        ])
    ], fluid=True, className="page-content py-4")

    dashboard_layout = html.Div([ 
        html.Main([header, main_content_area], className="content-below-topbar")
    ], 
    id='dashboard-wrapper', # Adicionado id para controle de posicionamento
    className="app-shell dark dashboard-container-wrapper", # Adicionado classe para estilo
    )

    # Layout final contém os dcc.Store e os dois wrappers
    # O container pai deve ter position: relative se os filhos forem absolute
    return html.Div([
        dcc.Location(id="url", refresh=True),
        dcc.Store(id='filtered-data-store'),
        dcc.Store(id='login-status-store'),
        login_layout,
        dashboard_layout
    ], style={'position': 'relative', 'height': '100vh', 'width': '100vw', 'overflow': 'hidden'}) # Container pai para posicionamento absoluto