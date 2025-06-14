# components/tabs/user_management_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_table # Importa dash_table para a tabela
from components.tabs.analysis_tab import create_page_header # Importe create_page_header

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
                dbc.Select( # NOVO: Dropdown para seleção de perfil
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
                dbc.Button("Recarregar Usuários", id="refresh-users-button", color="secondary", className="mb-3"), # Botão de refresh
                dash_table.DataTable(
                    id='user-history-table',
                    columns=[
                        {"name": "ID", "id": "id"},
                        {"name": "Nome de Usuário", "id": "username"},
                        {"name": "Perfil", "id": "profile"},
                        {"name": "Admin?", "id": "is_admin", "type": "any"}, # CORRIGIDO: "type": "boolean" para "type": "any"
                        {"name": "Ações", "id": "actions", "presentation": "markdown"}
                    ],
                    data=[], # Será populado por callback
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left', 'padding': '8px',
                        'backgroundColor': 'hsl(var(--card))', 'color': 'hsl(var(--foreground))',
                        'border': '1px solid hsl(var(--border))'
                    },
                    style_header={
                        'backgroundColor': 'hsl(var(--secondary))', 'color': 'hsl(var(--secondary-foreground))',
                        'fontWeight': 'bold', 'border': '1px solid hsl(var(--border))'
                    },
                    style_data_conditional=[
                        {'if': {'column_id': 'actions'}, 'textAlign': 'center'}, # Centraliza botões
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'hsl(var(--background), 0.5)'}
                    ]
                )
            ]),
            className="mb-4 content-card"
        ),

        # Modal para Edição de Usuário
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Editar Usuário")),
                dbc.ModalBody([
                    dbc.Input(id='edit-username-input', placeholder='Nome de Usuário', type='text', className='mb-3'),
                    dbc.Input(id='edit-password-input', placeholder='Nova Senha (deixe em branco para não alterar)', type='password', className='mb-3'),
                    dbc.Select( # NOVO: Dropdown para edição de perfil
                        id='edit-profile-dropdown',
                        options=PROFILE_OPTIONS,
                        placeholder='Selecione o Novo Perfil',
                        className='mb-3'
                    ),
                    dcc.Store(id='edit-user-id') # Armazena o ID do usuário sendo editado
                ]),
                dbc.ModalFooter([
                    dbc.Button("Salvar", id="save-user-edit-button", color="primary", className="ms-auto"),
                    dbc.Button("Cancelar", id="cancel-user-edit-button", color="secondary", className="ms-2")
                ]),
            ],
            id="user-edit-modal",
            is_open=False,
            size="md",
            backdrop=True, # Permite clicar fora para fechar
            keyboard=True # Permite fechar com a tecla Esc
        ),

        # Modal de Confirmação de Exclusão
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirmar Exclusão")),
                dbc.ModalBody("Tem certeza que deseja excluir este usuário?"),
                dbc.ModalFooter([
                    dbc.Button("Confirmar", id="confirm-delete-user-button", color="danger", className="ms-auto"),
                    dbc.Button("Cancelar", id="cancel-delete-user-button", color="secondary", className="ms-2")
                ]),
            ],
            id="confirm-delete-user-modal",
            is_open=False,
            size="sm"
        ),
        dcc.Store(id='delete-user-id-store') # Armazena o ID do usuário a ser deletado

    ])