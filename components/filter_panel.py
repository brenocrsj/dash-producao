# components/filter_panel.py
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd # Importar pandas para operar com datas

def create_filter_panel(df_full):
    # Calcula a data mínima e máxima presentes nos dados
    # Garante que 'Data_Apenas' é um formato de data para min/max funcionarem
    df_full['Data_Apenas'] = pd.to_datetime(df_full['Data_Apenas'])
    
    min_date = df_full['Data_Apenas'].min().date() # Converte para date() para o DatePickerRange
    max_date = df_full['Data_Apenas'].max().date() # Converte para date() para o DatePickerRange

    all_empresas = sorted(df_full['Empresa'].unique())
    all_destinos = sorted(df_full['Destino'].unique())
    all_materiais = sorted(df_full['Material'].unique())

    return dbc.Card(
        dbc.CardBody(
            [
                html.H4("Filtros", className="card-title mb-3"),
                dbc.Row([
                    dbc.Col(
                        html.Div([
                            dbc.Label("Período:"),
                            dcc.DatePickerRange(
                                id='date-picker-range',
                                start_date=min_date, # Inicializa com a data mínima dos dados
                                end_date=max_date,   # Inicializa com a data máxima dos dados
                                min_date_allowed=min_date, # Limite mínimo para seleção
                                max_date_allowed=max_date, # Limite máximo para seleção
                                display_format='DD/MM/YYYY',
                                calendar_orientation='horizontal',
                                className="dbc" # Classe para estilo Bootstrap
                            )
                        ], className="mb-3"),
                        md=6, lg=3 # Ocupa 6 colunas em telas médias, 3 em telas grandes
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Label("Empresa:"),
                            dcc.Dropdown(
                                id='empresa-dropdown',
                                options=[{'label': i, 'value': i} for i in all_empresas],
                                multi=True,
                                placeholder="Selecione a(s) empresa(s)",
                                className="dbc"
                            )
                        ], className="mb-3"),
                        md=6, lg=3
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Label("Destino:"),
                            dcc.Dropdown(
                                id='destino-dropdown',
                                options=[{'label': i, 'value': i} for i in all_destinos],
                                multi=True,
                                placeholder="Selecione o(s) destino(s)",
                                className="dbc"
                            )
                        ], className="mb-3"),
                        md=6, lg=3
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Label("Material:"),
                            dcc.Dropdown(
                                id='material-dropdown',
                                options=[{'label': i, 'value': i} for i in all_materiais],
                                multi=True,
                                placeholder="Selecione o(s) material(is)",
                                className="dbc"
                            )
                        ], className="mb-3"),
                        md=6, lg=3
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        dbc.Button("Limpar Filtros", id="clear-filters-button", color="secondary", className="mt-3 w-100"),
                        md=12, lg=3 # Botão ocupa 12 colunas em telas médias, 3 em telas grandes
                    )
                ])
            ]
        ),
        className="mb-4" # Margem inferior para o card de filtros
    )