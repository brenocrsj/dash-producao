from dash import html, dcc
import dash_bootstrap_components as dbc
import database # Importa o módulo para buscar os clientes

def create_shift_registration_layout():
    """Cria o layout do formulário de cadastro de turnos."""
    
    try:
        # Busca os clientes já cadastrados para popular o dropdown
        clients = database.get_all_clients()
        client_options = [{'label': client['name'], 'value': client['name']} for client in clients]
    except Exception as e:
        print(f"Erro ao buscar clientes para o formulário de turnos: {e}")
        client_options = [] # Se falhar, o dropdown ficará vazio

    return dbc.Card(
        dbc.CardBody([
            html.H5("Cadastrar Turno por Cliente", className="card-title"),
            dbc.Row([
                dbc.Col([
                    html.Label("Selecione o Cliente"),
                    dcc.Dropdown(id='shift-client-dropdown', options=client_options, placeholder="Cliente..."),
                ], md=6),
                dbc.Col([
                    html.Label("Nome do Turno (Ex: Turno 1, Turno da Manhã)"),
                    dbc.Input(id='shift-name-input', placeholder="Nome..."),
                ], md=6),
            ], className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Horário de Início"),
                    dbc.Input(id='shift-start-time-input', type='time', value="06:00"),
                ], md=6),
                dbc.Col([
                    html.Label("Horário de Fim"),
                    dbc.Input(id='shift-end-time-input', type='time', value="18:00"),
                ], md=6),
            ]),
            dbc.Button("Cadastrar Turno", id="register-shift-button", color="primary", className="mt-4"),
            html.Div(id="shift-registration-output", className="mt-3")
        ])
    )