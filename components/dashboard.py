# components/dashboard.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from config import THEME_COLORS # Importa as cores

# Importa as partes do layout que serão criadas em outros arquivos
from components.header import create_header_layout
from components.sidebar import create_sidebar_layout
from components.filter_panel import create_filter_panel
from components.tabs.analysis_tab import create_analysis_tab_layout # Sua aba de análise

def create_dashboard_layout(df_full: pd.DataFrame, df_meta_diaria: pd.DataFrame, df_meta_mes: pd.DataFrame, active_page='dashboard', logged_in_username='Usuário'):
    """
    Cria o layout principal do dashboard, incluindo header, sidebar e o conteúdo dinâmico.
    `active_page` é para destacar o item correto na sidebar.
    """
    # Definir o tema para este layout
    current_theme = 'light'
    colors = THEME_COLORS[current_theme]

    # Cria o cabeçalho (Header)
    header = create_header_layout(logged_in_username)

    # Cria a sidebar
    sidebar = create_sidebar_layout(active_page) # Passa a página ativa para a sidebar

    # Cria o painel de filtros (este painel deve ser global no dashboard)
    filter_panel = create_filter_panel(df_full) # Não precisa passar o tema explicitamente, ele pega do config

    # Conteúdo da página principal (depende da rota ou da aba ativa)
    main_page_content = html.Div(id="main-page-content", children=[
        # Por padrão, vamos mostrar o create_analysis_tab_layout
        create_analysis_tab_layout(df_full, current_theme, df_meta_diaria, df_meta_mes)
    ])

    # Área de conteúdo principal do dashboard (filtros + main_page_content)
    main_content_area = html.Main(
        className="main-dashboard-content", # Classe para o CSS
        children=[
            filter_panel, # Painel de filtros no topo da main area
            main_page_content # Conteúdo dinâmico da página/aba
        ]
    )

    # Layout do dashboard completo (header + sidebar + main_content_area)
    return html.Div(
        [
            header, # O header superior
            html.Div(
                className="container-app-flex", # Classe para o flexbox que contém sidebar e main
                children=[
                    sidebar, # A barra lateral
                    main_content_area # O conteúdo principal do dashboard
                ]
            ),
            html.Footer( # Rodapé conforme seu HTML de exemplo
                "© 2025 FleetMaster. Todos os direitos reservados.",
                className="app-footer"
            )
        ],
        className="dashboard-wrapper-inner" # Wrapper interno do dashboard para CSS se precisar
    )