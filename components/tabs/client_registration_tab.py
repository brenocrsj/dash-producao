# components/tabs/client_registration_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from components.common_components import create_page_header
import database
from dash import dash_table
from config import THEME_COLORS # <<< ESSA IMPORTAÇÃO É CRUCIAL


def create_client_registration_layout(dff, theme='dark'):
    """
    Cria o layout para a aba de 'Cadastro de Clientes',
    incluindo formulário de registro, lista de destinos sem cliente
    e a tabela de clientes cadastrados.
    """
    colors = THEME_COLORS[theme] # <<< ESSA LINHA DEVE ESTAR ASSIM
    # ... (restante do código) ...

    # Lógica para obter destinos únicos da planilha e clientes existentes
    unique_destinations_from_df = sorted(dff['Destino'].dropna().unique()) if 'Destino' in dff.columns else []
    
    # Obter destinos já cadastrados no banco de dados
    registered_clients_db = database.get_all_clients()
    registered_destinations = {client['destination'] for client in registered_clients_db}

    # Identificar destinos sem cliente
    destinations_without_client = [
        dest for dest in unique_destinations_from_df 
        if dest not in registered_destinations
    ]

    # Preparar dados para a dash_table.DataTable de clientes cadastrados
    clients_table_data = []
    clients_table_columns = []
    if registered_clients_db:
        clients_table_data = [dict(row) for row in registered_clients_db]
        clients_table_columns = [{"name": "ID", "id": "id"}, {"name": "Cliente", "id": "client_name"}, {"name": "Destino", "id": "destination"}]


    return html.Div([
        create_page_header("Cadastro de Clientes", "Registre novos clientes e veja destinos sem associação."),
        
        # Formulário de Cadastro de Cliente
        dbc.Card(
            dbc.CardBody([
                html.H4("Registrar Novo Cliente", className="card-title mb-3"),
                dbc.Row([
                    dbc.Col(
                        dbc.Input(id="client-name-input", placeholder="Nome do Cliente", type="text", className="mb-3"),
                        md=6
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="destination-dropdown",
                            options=[{'label': dest, 'value': dest} for dest in destinations_without_client],
                            placeholder="Selecione ou digite um Destino",
                            className="mb-3",
                            multi=False,
                            searchable=True
                        ),
                        md=6
                    ),
                ]),
                dbc.Button("Cadastrar Cliente", id="register-client-button", color="primary", className="mt-2"),
                html.Div(id="client-registration-output", className="mt-3")
            ]),
            className="content-card mb-4"
        ),

        # Tabela/Lista de Destinos Sem Cliente
        dbc.Card(
            dbc.CardBody([
                html.H4("Destinos sem Cliente Cadastrado", className="card-title mb-3"),
                html.P("Estes destinos aparecem nos seus dados de volume, mas não estão vinculados a um cliente registrado.", className="chart-card-description mb-3"),
                html.Div([
                    dbc.ListGroup([
                        dbc.ListGroupItem(dest, color="danger") for dest in destinations_without_client
                    ]) if destinations_without_client else html.P("Todos os destinos têm clientes cadastrados ou não há destinos nos dados.")
                ], id="destinations-without-client-list")
            ]),
            className="content-card mb-4"
        ),

        # Tabela de Clientes Cadastrados
        dbc.Card(
            dbc.CardBody([
                html.H4("Clientes Cadastrados", className="card-title mb-3"),
                html.P("Lista de todos os clientes registrados e seus destinos associados.", className="chart-card-description mb-3"),
                dash_table.DataTable(
                    id='registered-clients-table',
                    columns=clients_table_columns,
                    data=clients_table_data,
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': colors['card_bg'], # <<< AQUI AGORA VAI FUNCIONAR
                        'color': colors['text'],             # <<< AQUI TAMBÉM
                        'border': f'1px solid {colors["border"]}'
                    },
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': colors['foreground'], # Usar 'foreground' para texto do cabeçalho
                        'fontWeight': 'bold',
                        'border': f'1px solid {colors["border"]}'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'hsla(0, 0%, 90%, 0.1)'}, # Exemplo de fundo mais claro para linhas ímpares em tema dark
                    ]
                )
            ]),
            className="content-card mb-4"
        )
    ])