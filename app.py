# app.py

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

# 1. Importações da nossa estrutura modular
from logic.data_processing import load_and_prepare_data
from logic.callbacks import register_callbacks
from components.sidebar import create_sidebar
from components.header import create_header
from components.filter_panel import create_filter_panel
# A importação de 'create_tabs' não é mais necessária

# 2. Carregamento de Dados
df = load_and_prepare_data()

# 3. Inicialização do App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
app.title = "FleetMaster - Análise Operacional"

# 4. Criação dos componentes
sidebar = create_sidebar()
header = create_header()

# O conteúdo principal agora tem o painel de filtros e um container para a página
main_content_area = html.Div([
    dcc.Store(id='filtered-data-store'), # <-- O Store voltou!
    create_filter_panel(df),             # <-- O painel de filtros voltou!
    html.Div(id='page-content')          # <-- Container para o conteúdo dinâmico
], className="page-content")

content = html.Main([header, main_content_area], className="content")

# 5. Layout Final
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    sidebar,
    content
], className="app-shell dark")

# 6. Registro de todos os Callbacks
register_callbacks(app, df)