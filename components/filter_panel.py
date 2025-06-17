# components/filter_panel.py

import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

def create_filter_panel(df):
    """
    Cria e retorna APENAS o Card com os componentes de filtro.
    A lógica de visibilidade foi movida para o layout e callbacks principais.
    """
    # Obtenção de valores únicos para os dropdowns
    empresas = sorted(df['Empresa'].dropna().unique()) if 'Empresa' in df.columns else []
    destinos = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
    materiais = sorted(df['Material'].dropna().unique()) if 'Material' in df.columns else []

    # Retorna diretamente o Card com todos os filtros
    return dbc.Card(
        dbc.CardBody([
            html.H5("Filtros", className="card-title mb-3"),
            
            html.Label("Período:", className="form-label"),
            dcc.DatePickerRange(
                id='date-picker-range',
                display_format='DD/MM/YYYY',
                month_format='MMMM YYYY',
                start_date_placeholder_text="Início",
                end_date_placeholder_text="Fim",
                clearable=True,
                className="mb-3 w-100"
            ),

            html.Label("Empresa:", className="form-label"),
            dcc.Dropdown(
                id='empresa-dropdown',
                options=[{'label': i, 'value': i} for i in empresas],
                multi=True,
                placeholder="Selecione...",
                className="mb-3"
            ),

            html.Label("Destino:", className="form-label"),
            dcc.Dropdown(
                id='destino-dropdown',
                options=[{'label': i, 'value': i} for i in destinos],
                multi=True,
                placeholder="Selecione...",
                className="mb-3"
            ),

            html.Label("Material:", className="form-label"),
            dcc.Dropdown(
                id='material-dropdown',
                options=[{'label': i, 'value': i} for i in materiais],
                multi=True,
                placeholder="Selecione...",
                className="mb-3"
            ),
            
            # O botão de limpar filtros permanece aqui, o que está correto.
            dbc.Button("Limpar Filtros", id="clear-filters-button", color="secondary", className="mt-3 w-100"),
        ]),
        className="h-100"  # Classe para fazer o card ocupar a altura da coluna
    )