# components/tabs/user_management_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table # CORREÇÃO 1: Importação correta do dash_table

# CORREÇÃO 2: Importando do arquivo de componentes comuns que criamos
from components.common_components import create_page_header

# Opções de perfil de usuário
PROFILE_OPTIONS = [
    {'label': 'Administrador', 'value': 'admin'},
    {'label': 'Analista', 'value': 'analyst'},
    {'label': 'Operador', 'value': 'operator'}
]

def create_user_management_layout():
    """Cria o layout para a aba de Gerenciamento de Usuários."""
    return html.Div([
        create_page_header("Gestão de Usuários", "Crie, gerencie e edite usuários do sistema."),
        
        # Seção para Mensagens de Feedback
        html.Div(id='user-management-message', className='mt-3 mb-3'),

        # Cartão para Criar Novo Usuário
        dbc.Card(
            dbc.CardBody([
                html.H4("Criar Novo Usuário", className="card-title mb-3"),
                dbc.Input(id='new-username-input', placeholder='Nome de Usuário', type='text', className='mb-3'),
                dbc.Input(id='new-password-input', placeholder='Senha', type='password', className='mb-3'),
                dbc.Select(
                    id='new-profile-dropdown',
                    options=PROFILE_OPTIONS,
                    value='analyst', # Perfil padrão
                    placeholder='Selecione o Perfil',
                    className='mb-3'
                ),
                dbc.Button('Criar Usuário', id='create-user-button', color='primary', className='w-100'),
            ]),
            className="mb-4 content-card"
        ),

        # Cartão para Histórico de Usuários
        dbc.Card(
            dbc.CardBody([
                html.H4("Histórico de Usuários", className="card-title mb-3"),
                dbc.Button("Recarregar Usuários", id="refresh-users-button", color="secondary", className="mb-3"),
                dash_table.DataTable(
                    id='user-history-table',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Nome de Usuário", "id": "username"},
                        {"name": "Perfil", "id": "profile"},
                        {"name": "Admin?", "id": "is_admin", "type": "any"},
                        {"name": "Ações", "id": "actions", "presentation": "markdown"}
                    ],
                    data=[],
                    editable=False, filter_action="native", sort_action="native", page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '8px', 'backgroundColor': 'transparent', 'color': 'hsl(var(--foreground))', 'border': '1px solid hsl(var(--border))'},
                    style_header={'backgroundColor': 'hsl(var(--secondary))', 'color': 'hsl(var(--foreground))', 'fontWeight': 'bold', 'border': '1px solid hsl(var(--border))'},
                    style_data_conditional=[
                        {'if': {'column_id': 'actions'}, 'textAlign': 'center'},
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'hsla(var(--secondary), 0.3)'}
                    ]
                )
            ]),
            className="mb-4 content-card"
        ),

        # Modais (nenhuma alteração necessária aqui)
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Editar Usuário")),
                dbc.ModalBody([
                    dbc.Input(id='edit-username-input', placeholder='Nome de Usuário', type='text', className='mb-3'),
                    dbc.Input(id='edit-password-input', placeholder='Nova Senha (deixe em branco para não alterar)', type='password', className='mb-3'),
                    dbc.Select(id='edit-profile-dropdown', options=PROFILE_OPTIONS, placeholder='Selecione o Novo Perfil', className='mb-3'),
                    dcc.Store(id='edit-user-id')
                ]),
                dbc.ModalFooter([
                    dbc.Button("Salvar", id="save-user-edit-button", color="primary"),
                    dbc.Button("Cancelar", id="cancel-user-edit-button", color="secondary")
                ]),
            ],
            id="user-edit-modal", is_open=False,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirmar Exclusão")),
                dbc.ModalBody("Tem certeza que deseja excluir este usuário?"),
                dbc.ModalFooter([
                    dbc.Button("Confirmar", id="confirm-delete-user-button", color="danger"),
                    dbc.Button("Cancelar", id="cancel-delete-user-button", color="secondary")
                ]),
            ],
            id="confirm-delete-user-modal", is_open=False,
        ),
        dcc.Store(id='delete-user-id-store')

    ])