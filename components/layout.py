# components/layout.py
from dash import html, dcc
from .auth_layout import create_auth_layout
from .sidebar import create_sidebar
from .header import create_header
from .filter_panel import create_filter_panel

def create_main_layout(df_full):
    """Cria o layout base COMPLETO da aplicação, com ambas as visualizações."""
    
    # Wrapper para a tela de autenticação
    login_layout = html.Div(
        create_auth_layout(),
        id='login-wrapper',
        # A visibilidade será controlada por um callback
    )

    # Wrapper para o dashboard principal
    sidebar = create_sidebar()
    header = create_header()
    page_content_container = html.Div(id="page-content-container")
    
    main_content_area = html.Div([
        create_filter_panel(df_full),
        page_content_container 
    ], className="page-content")

    dashboard_layout = html.Div([
        sidebar, 
        html.Main([header, main_content_area], className="content")
    ], 
    id='dashboard-wrapper',
    className="app-shell dark",
    )

    # Layout final contém o dcc.Store e os dois wrappers
    return html.Div([
        dcc.Location(id="url", refresh=True),
        dcc.Store(id='filtered-data-store'),
        login_layout,
        dashboard_layout
    ])