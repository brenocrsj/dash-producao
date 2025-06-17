# components/filter_panel.py
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd # Certifique-se de que o pandas está importado

def create_filter_panel(df):
    """Cria o painel de filtros do dashboard."""
    # Obter opções únicas para os dropdowns
    empresas = sorted(df['Empresa'].dropna().unique()) if 'Empresa' in df.columns else []
    destinos = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
    materiais = sorted(df['Material'].dropna().unique()) if 'Material' in df.columns else []

    return dbc.Card(
        dbc.CardBody([
            html.H5("Filtros", className="card-title mb-3"),
            html.Label("Período:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text="Data de Início",
                end_date_placeholder_text="Data Final",
                display_format='DD/MM/YYYY',
                month_format='MMMMYYYY',
                clearable=True,
                className="mb-3"
            ),
            html.Label("Empresa:"),
            dcc.Dropdown(
                id='empresa-dropdown',
                options=[{'label': i, 'value': i} for i in empresas],
                multi=True,
                placeholder="Selecione a(s) empresa(s)",
                className="mb-3"
            ),
            html.Label("Destino:"),
            dcc.Dropdown(
                id='destino-dropdown',
                options=[{'label': i, 'value': i} for i in destinos],
                multi=True,
                placeholder="Selecione o(s) destino(s)",
                className="mb-3"
            ),
            html.Label("Material:"),
            dcc.Dropdown(
                id='material-dropdown',
                options=[{'label': i, 'value': i} for i in materiais],
                multi=True,
                placeholder="Selecione o(s) material(is)",
                className="mb-3"
            ),
            dbc.Button("Limpar Filtros", id="clear-filters-button", color="secondary", className="mt-3 me-2"), # Adicionado me-2 para espaçamento
            dbc.Button(
                [html.I(className="bi bi-arrows-angle-contract"), " Esconder Filtro"], # Ícone e texto
                id="toggle-filter-button", 
                color="info", 
                className="mt-3"
            ) # <<< ADICIONADO AQUI: Botão para esconder/mostrar filtro
        ]),
        className="content-card"
    )