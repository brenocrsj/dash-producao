# logic/callbacks.py

# --- 1. IMPORTAÇÕES ---
from dash import Input, Output, State, html, dcc, exceptions
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO
from flask_login import login_user, logout_user, current_user
from urllib.parse import parse_qs

import database
from components.sidebar import SIDEBAR_NAV_ITEMS # Importa os itens de navegação da sidebar
from components.tabs.analysis_tab import create_analysis_tab_layout, create_page_header
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout
from components.tabs.user_management_tab import create_user_management_layout
from flask_login import login_user, logout_user, current_user # Mantenha esta importação


# --- 2. FUNÇÃO DE REGISTRO DE CALLBACKS ---
def register_callbacks(app, df):
    """
    Agrupa e registra todos os callbacks da aplicação Dash.
    
    Args:
        app: A instância da aplicação Dash.
        df: O DataFrame completo dos dados pré-processados.
    """

    # --- CALLBACK 1: CONTROLE DE VISIBILIDADE DE AUTENTICAÇÃO ---
    # Gerencia a exibição da tela de login ou do dashboard principal
    @app.callback(
        Output('login-wrapper', 'style'),
        Output('dashboard-wrapper', 'style'),
        Output('login-status-store', 'data'), # Atualiza o status de login no store
        Input('url', 'pathname')
    )
    def master_visibility_router(pathname):
        """
        Controla a visibilidade dos wrappers de login e dashboard.
        Mostra o dashboard se o usuário estiver autenticado, caso contrário, mostra a tela de login.
        Também atualiza o status de login no dcc.Store.
        """
        if current_user.is_authenticated:
            # Se logado, esconde o login e mostra o dashboard
            # Armazena o status de admin no store
            return {'display': 'none'}, {'display': 'block'}, {'is_authenticated': True, 'is_admin': current_user.is_admin, 'username': current_user.username}
        
        # Se não logado, mostra o login e esconde o dashboard
        return {'display': 'flex'}, {'display': 'none'}, {'is_authenticated': False, 'is_admin': False, 'username': None}


    # --- CALLBACK 2: RENDERIZADOR DE CONTEÚDO DA PÁGINA E TÍTULO ---
    # Atualiza o conteúdo e o título da página com base na URL e nos dados filtrados
    @app.callback(
        Output('page-content-container', 'children'),
        Output('page-title', 'children'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content_and_title(pathname, jsonified_data):
        """
        Renderiza o conteúdo da página e atualiza o título com base na URL.
        Converte o JSON dos dados filtrados de volta para DataFrame.
        """
        if not current_user.is_authenticated:
            # Impede a atualização se o usuário não estiver autenticado
            raise exceptions.PreventUpdate

        # Converte dados filtrados (JSON) de volta para DataFrame
        # Se não houver dados filtrados, usa o DataFrame completo
        if jsonified_data:
            dff = pd.read_json(StringIO(jsonified_data), orient='split')
        else:
            dff = df.copy()
        
        # Reconverte colunas de data/hora após a desserialização do JSON
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div() # Conteúdo padrão vazio
        page_title = "Página não encontrada" # Título padrão
        
        # Roteamento de conteúdo com base no pathname
        if pathname == "/":
            page_content, page_title = create_analysis_tab_layout(dff, 'dark'), "Análise Geral"
        elif pathname == "/matrix":
            page_content, page_title = create_matrix_tab_layout(dff, 'dark'), "Análise Matricial"
        elif pathname == "/efficiency":
            page_content, page_title = create_efficiency_tab_layout(dff, 'dark'), "Análise de Eficiência"
        elif pathname == "/management/users":
            # Proteção adicional no lado do servidor para a página de gestão de usuários
            if not current_user.is_admin:
                return dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4"), "Acesso Negado"
            page_content, page_title = create_user_management_layout(), "Gestão de Usuários"
        elif pathname in ["/management/equipment", "/settings"]:
            page_title = next(
                (item["title"] for item in SIDEBAR_NAV_ITEMS if item["href"] == pathname),
                "Página"
            )
            page_content = html.Div([
                create_page_header(page_title, "Funcionalidade em desenvolvimento."),
                dbc.Alert("Em breve.", color="info", className="m-4")
            ])
        elif pathname == "/logout":
            logout_user() # Desloga o usuário
            return dcc.Location(pathname="/login", id="redirect-logout"), "Saindo..."
        else:
            page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        
        return page_content, page_title


    # --- CALLBACK 3: LÓGICA DE LOGIN ---
    @app.callback(
        Output('url', 'pathname'),
        Output('login-output', 'children'),
        Input('login-button', 'n_clicks'),
        State('username-input', 'value'),
        State('password-input', 'value'),
        State('remember-me-checkbox', 'value'),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password, remember_me_value):
        print(f"DEBUG: handle_login acionado. N_clicks: {n_clicks}, User: {username}, Pass: {'*' * len(str(password))}, Remember: {remember_me_value}")

        if not username or not password:
            print("DEBUG: Campos de usuário/senha vazios.")
            return exceptions.no_update, dbc.Alert("Preencha todos os campos.", color="warning", duration=3000)

        user = database.get_user_by_username(username)
        print(f"DEBUG: database.get_user_by_username retornou: {user.username if user else 'None'}")
        
        remember = 1 in remember_me_value

        if user and database.check_password(user.password_hash, password):
            print(f"DEBUG: Senha correta para {username}. Tentando login_user.")
            login_user(user, remember=remember)
            print(f"DEBUG: login_user chamado para {username}. Redirecionando para /.")
            return "/", ""
        else:
            print(f"DEBUG: Nome de usuário ou senha inválidos para {username}.")
            return exceptions.no_update, dbc.Alert("Nome de usuário ou senha inválidos.", color="danger", duration=3000)

    # --- CALLBACK 4: CADASTRO INTERNO DE USUÁRIO ---
    # Permite o cadastro de novos usuários através da interface de gestão
    @app.callback(
        Output('user-management-message', 'children'),
        Input('create-user-button', 'n_clicks'),
        State('new-username-input', 'value'),
        State('new-password-input', 'value'),
        prevent_initial_call=True
    )
    def handle_internal_registration(n_clicks, username, password):
        """
        Gerencia o processo de criação de novos usuários no sistema.
        Retorna mensagens de sucesso ou erro.
        """
        if not username or not password:
            return dbc.Alert(
                "Nome de usuário e senha são obrigatórios.",
                color="warning",
                duration=4000
            )
        
        if database.add_user(username, password):
            return dbc.Alert(
                f"Usuário '{username}' criado com sucesso!",
                color="success",
                duration=4000
            )
        
        return dbc.Alert(
            f"O nome de usuário '{username}' já existe.",
            color="danger",
            duration=4000
        )


    # --- CALLBACK 5: ATUALIZAÇÃO DOS DADOS FILTRADOS ---
    # Filtra o DataFrame principal com base nas seleções do usuário
    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('empresa-dropdown', 'value'),
        Input('destino-dropdown', 'value'),
        Input('material-dropdown', 'value')
    )
    def update_filtered_data(start_date, end_date, empresas, destinos, materiais):
        """
        Atualiza o dcc.Store com os dados filtrados.
        Aplica filtros de data, empresa, destino e material.
        """
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate

        dff = df.copy() # Começa com uma cópia do DataFrame completo
        
        # Aplica filtros sequencialmente
        if start_date and end_date:
            dff = dff[
                (dff['Data_Apenas'] >= pd.to_datetime(start_date).date()) &
                (dff['Data_Apenas'] <= pd.to_datetime(end_date).date())
            ]
        
        if empresas:
            dff = dff[dff['Empresa'].isin(empresas)]
        
        if destinos:
            dff = dff[dff['Destino'].isin(destinos)]
        
        if materiais:
            dff = dff[dff['Material'].isin(materiais)]
        
        # Retorna o DataFrame filtrado como JSON para o dcc.Store
        return dff.to_json(date_format='iso', orient='split')


    # --- CALLBACK 6: LIMPAR FILTROS ---
    # Redefine todos os filtros para seus estados iniciais (mostrando todos os dados)
    @app.callback(
        Output('filtered-data-store', 'data', allow_duplicate=True),
        Output('date-picker-range', 'start_date'),
        Output('date-picker-range', 'end_date'),
        Output('empresa-dropdown', 'value'),
        Output('destino-dropdown', 'value'),
        Output('material-dropdown', 'value'),
        Input('clear-filters-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_all_filters(n_clicks):
        """
        Limpa todos os filtros de data, empresa, destino e material,
        restaurando os dados completos no dcc.Store.
        """
        # Define as datas inicial e final para os limites do DataFrame original
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        
        # Retorna o DataFrame completo e valores vazios para os filtros
        return df.to_json(date_format='iso', orient='split'), \
               start_date, end_date, \
               [], [], []

    # --- CALLBACK 7: TOGGLE DA BARRA LATERAL ---
    @app.callback(
        Output('dashboard-wrapper', 'className'), # Altera a classe do wrapper principal
        Output('sidebar-toggle-button', 'children'), # Altera o ícone do botão
        Input('sidebar-toggle-button', 'n_clicks'),
        State('dashboard-wrapper', 'className'),
        prevent_initial_call=True
    )
    def toggle_sidebar(n_clicks, current_dashboard_class):
        """
        Alterna a classe 'sidebar-minimized' na sidebar e o ícone do botão de toggle.
        """
        if n_clicks is None:
            raise exceptions.PreventUpdate

        # Alterna a classe 'sidebar-minimized' no dashboard-wrapper
        if 'sidebar-minimized' in current_dashboard_class:
            new_class = current_dashboard_class.replace(' sidebar-minimized', '')
            button_icon = html.I(className="bi bi-list", style={"font-size": "1.5rem"}) # Ícone de hamburguer
        else:
            new_class = current_dashboard_class + ' sidebar-minimized'
            button_icon = html.I(className="bi bi-x-lg", style={"font-size": "1.5rem"}) # Ícone de X

        return new_class, button_icon

    # --- CALLBACK 8: VISIBILIDADE DO LINK DE GESTÃO DE USUÁRIOS E NOME DE USUÁRIO NA SIDEBAR ---
    @app.callback(
        Output('nav-link-user-management', 'style'), # Esconde/mostra o link de gestão de usuários
        Output('sidebar-user-info', 'children'), # Atualiza o nome do usuário no rodapé da sidebar
        Input('login-status-store', 'data'), # Disparado quando o status de login muda
    )
    def update_user_management_link_and_info(login_status):
        """
        Controla a visibilidade do link 'Gestão de Usuários' com base no status de admin
        e atualiza o nome do usuário logado na sidebar.
        """
        if login_status and login_status.get('is_authenticated'):
            username = login_status.get('username', 'Usuário')
            user_info_text = html.Span(
                f"Logado como: {username.capitalize()}",
                className="text-muted small"
            )
            if login_status.get('is_admin'):
                return {'display': 'flex'}, user_info_text # Mostra o link para admins
            else:
                return {'display': 'none'}, user_info_text # Esconde para não-admins
        else:
            # Caso não esteja autenticado ou status não disponível
            return {'display': 'none'}, "Não logado" # Esconde o link e mostra "Não logado"
