# components/tabs/pricing_registration_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from components.common_components import create_page_header
import database
from dash import dash_table
from config import THEME_COLORS 

def create_pricing_registration_layout(dff, theme='dark'):
    """
    Cria o layout para a aba de 'Cadastro de Precificação',
    incluindo formulário de registro de preços e tabela de preços cadastrados.
    """
    colors = THEME_COLORS[theme]

    # Lógica para obter destinos únicos da planilha para o dropdown
    unique_destinations_from_df = sorted(dff['Destino'].dropna().unique()) if 'Destino' in dff.columns else []

    # Obter todas as precificações já cadastradas para exibir na tabela
    registered_pricing_db = database.get_all_pricing()
    pricing_table_data = []
    pricing_table_columns = []
    if registered_pricing_db:
        pricing_table_data = [dict(row) for row in registered_pricing_db]
        # Define as colunas da tabela de forma mais amigável
        pricing_table_columns = [
            {"name": "ID", "id": "id"},
            {"name": "Destino", "id": "destination"},
            {"name": "Preço/Ton", "id": "price_per_ton", "type": "numeric", "format": {"specifier": "$.2f"}}, # Formato monetário
            {"name": "Data Início", "id": "start_date", "type": "datetime"},
            {"name": "Data Fim", "id": "end_date", "type": "datetime"}
        ]
        # Formata o preço para duas casas decimais no display
        for row in pricing_table_data:
            if 'price_per_ton' in row and pd.notnull(row['price_per_ton']):
                row['price_per_ton'] = f"{row['price_per_ton']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


    return html.Div([
        create_page_header("Cadastro de Precificação", "Gerencie o valor por tonelada de cada destino por período."),
        
        # Formulário de Cadastro de Precificação
        dbc.Card(
            dbc.CardBody([
                html.H4("Registrar Nova Precificação", className="card-title mb-3"),
                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id="pricing-destination-dropdown",
                            options=[{'label': dest, 'value': dest} for dest in unique_destinations_from_df],
                            placeholder="Selecione um Destino",
                            className="mb-3",
                            multi=False,
                            searchable=True
                        ),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Input(id="price-per-ton-input", placeholder="Preço por Tonelada (ex: 123.45)", type="number", min=0, step=0.01, className="mb-3"),
                        md=4
                    ),
                ]),
                dbc.Row([
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id='start-date-picker',
                            placeholder="Data de Início",
                            display_format='DD/MM/YYYY',
                            month_format='MMMM YYYY',
                            clearable=True,
                            className="mb-3"
                        ),
                        md=4
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(
                            id='end-date-picker',
                            placeholder="Data Final",
                            display_format='DD/MM/YYYY',
                            month_format='MMMM YYYY',
                            clearable=True,
                            className="mb-3"
                        ),
                        md=4
                    ),
                ]),
                dbc.Button("Cadastrar Preço", id="register-price-button", color="primary", className="mt-2"),
                html.Div(id="pricing-registration-output", className="mt-3") # Feedback para o usuário
            ]),
            className="content-card mb-4"
        ),

        # Tabela de Precificações Cadastradas
        dbc.Card(
            dbc.CardBody([
                html.H4("Precificações Cadastradas", className="card-title mb-3"),
                html.P("Lista de todos os valores por tonelada registrados para cada destino e período.", className="chart-card-description mb-3"),
                dash_table.DataTable(
                    id='registered-pricing-table', # ID para a tabela
                    columns=pricing_table_columns,
                    data=pricing_table_data,
                    page_size=10, # Limite de linhas por página
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': colors['card_bg'],
                        'color': colors['text'],
                        'border': f'1px solid {colors["border"]}'
                    },
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': colors['foreground'],
                        'fontWeight': 'bold',
                        'border': f'1px solid {colors["border"]}'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'hsla(0, 0%, 90%, 0.1)'}, # Fundo mais claro para linhas ímpares
                    ]
                )
            ]),
            className="content-card mb-4"
        )
    ])