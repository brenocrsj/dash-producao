# components/filter_panel.py (versão corrigida e completa)

from dash import dcc
import dash_bootstrap_components as dbc

def create_filter_panel(df):
    """
    Cria o painel de filtros completo, incluindo todos os dropdowns necessários.
    """
    return dbc.Card(className="filter-panel", body=True, children=[
        dbc.Row([
            # Filtro de Data
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['Data_Hora'].min().date(),
                max_date_allowed=df['Data_Hora'].max().date(),
                start_date=df['Data_Hora'].min().date(),
                end_date=df['Data_Hora'].max().date(),
                display_format='DD/MM/YYYY',
                className="date-picker-style"
            ), width=12, lg=4, className="mb-3"),
            
            # Filtro de Empresa (ESTAVA FALTANDO)
            dbc.Col(dcc.Dropdown(
                id='empresa-dropdown',
                multi=True,
                placeholder='Filtrar por Empresa...',
                options=[{'label': i, 'value': i} for i in df['Empresa'].dropna().unique()]
            ), width=12, lg=2, className="mb-3"),
            
            # Filtro de Destino (PROVAVELMENTE FALTANDO TAMBÉM)
            dbc.Col(dcc.Dropdown(
                id='destino-dropdown',
                multi=True,
                placeholder='Filtrar por Destino...',
                options=[{'label': i, 'value': i} for i in df['Destino'].dropna().unique()]
            ), width=12, lg=3, className="mb-3"),

            # Filtro de Material
            dbc.Col(dcc.Dropdown(
                id='material-dropdown',
                multi=True,
                placeholder='Filtrar por Material...',
                options=[{'label': i, 'value': i} for i in df['Material'].dropna().unique()]
            ), width=12, lg=3, className="mb-3"),
        ]),
        dbc.Row([
            # Botão para Limpar Filtros
            dbc.Col(dbc.Button("Limpar Todos os Filtros", id='clear-filters-button', color="primary", className="w-100"), 
                    width=12)
        ])
    ])