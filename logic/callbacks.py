# logic/callbacks.py

# --- 1. IMPORTAÇÕES ---
from dash import Input, Output, State, html, dcc, exceptions
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO
from flask_login import login_user, logout_user, current_user
from urllib.parse import parse_qs

import database
from components.header import TOPBAR_NAV_ITEMS # Importa os itens de navegação da nova barra superior
from components.tabs.analysis_tab import create_analysis_tab_layout, create_page_header
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout
from components.tabs.user_management_tab import create_user_management_layout


# --- 2. FUNÇÃO DE REGISTRO DE CALLBACKS ---
def register_callbacks(app, df):
    """Agrupa e registra todos os callbacks da aplicação."""

    # CALLBACK 1: O "PORTEIRO" DE VISIBILIDADE
    @app.callback(
        Output('login-wrapper', 'style'),
        Output('dashboard-wrapper', 'style'),
        Output('login-status-store', 'data'),
        Input('url', 'pathname')
    )
    def master_visibility_router(pathname):
        if current_user.is_authenticated:
            # Se logado, esconde o login e mostra o dashboard
            # Armazena o status de admin no store
            return {'display': 'none'}, {'display': 'block'}, {'is_authenticated': True, 'is_admin': current_user.is_admin, 'username': current_user.username}
        
        # Se não logado, mostra o login e esconde o dashboard
        return {'display': 'flex'}, {'display': 'none'}, {'is_authenticated': False, 'is_admin': False, 'username': None}


    # CALLBACK 2: RENDERIZADOR DE CONTEÚDO E TÍTULO
    @app.callback(
        Output('page-content-container', 'children'),
        # REMOVIDO: Output('page-title', 'children'), # Removido pois page-title não existe mais como um ID no layout central
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content_and_title(pathname, jsonified_data):
        if not current_user.is_authenticated:
            # Se o pathname é /logout, mas não está autenticado, apenas redireciona para login
            if pathname == "/logout":
                return dcc.Location(pathname="/login", id="redirect-logout-not-auth"), "Redirecionando..."
            raise exceptions.PreventUpdate # Impede atualização se não logado e não é logout

        # Converte dados filtrados (JSON) de volta para DataFrame
        # Se não houver dados filtrados, usa o DataFrame completo
        dff = pd.read_json(StringIO(jsonified_data), orient='split') if jsonified_data else df.copy()
        # Reconverte colunas de data/hora após a desserialização do JSON
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div()
        # page_title = "Página não encontrada" # Esta variável não é mais um Output, mas pode ser usada para debug interno
        
        # Roteamento de conteúdo com base no pathname
        if pathname == "/":
            page_content = create_analysis_tab_layout(dff, 'dark')
            # page_title = "Análise Geral"
        elif pathname == "/matrix":
            page_content = create_matrix_tab_layout(dff, 'dark')
            # page_title = "Análise Matricial"
        elif pathname == "/efficiency":
            page_content = create_efficiency_tab_layout(dff, 'dark')
            # page_title = "Análise de Eficiência"
        elif pathname == "/management/users":
            # Proteção adicional no lado do servidor para a página de gestão de usuários
            if not current_user.is_admin:
                return dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4")
            page_content = create_user_management_layout()
            # page_title = "Gestão de Usuários"
        elif pathname in ["/management/equipment", "/settings"]:
            page_title_text = next((item["label"] for item in TOPBAR_NAV_ITEMS if item["href"] == pathname), "Página")
            page_content = html.Div([create_page_header(page_title_text, f"Funcionalidade em desenvolvimento."), dbc.Alert("Em breve.", color="info", className="m-4")])
            # page_title = page_title_text
        elif pathname == "/logout":
            logout_user() # Desloga o usuário
            # Usa o estilo do card de login para a tela de logout
            page_content = html.Div(
                className="auth-container-background", # Usa a classe de fundo da tela de login
                children=[
                    dbc.Card(
                        [
                            html.Div(
                                html.Img(src="/assets/logo_fleetmaster.png", className="login-logo"),
                                className="login-logo-container"
                            ),
                            html.Div(
                                html.H2("Saindo...", className="text-center mb-4 logout-title"), # Título de saída
                                className="mb-4"
                            ),
                            # Ícone de carregamento ou algo mais visual
                            html.Div(dbc.Spinner(size="lg", color="primary", type="grow"), className="text-center mb-3"),
                            dcc.Location(id="redirect-logout", refresh=True), # O Location para redirecionar
                            dcc.Interval(id="logout-interval", interval=500, n_intervals=0, max_intervals=1) # Redireciona após 0.5s
                        ],
                        className="auth-card login-card-border" # Usa as classes de card de login
                    )
                ]
            )
            # page_title = "Saindo..."
        else:
            page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        
        return page_content

    # NOVO CALLBACK: Para forçar a redireção após o intervalo na tela de logout
    @app.callback(
        Output('redirect-logout', 'pathname'),
        Input('logout-interval', 'n_intervals'),
        prevent_initial_call=True
    )
    def perform_logout_redirect(n_intervals):
        if n_intervals > 0:
            return "/login"
        raise exceptions.PreventUpdate


    # CALLBACK 3: LÓGICA DE LOGIN
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

    # CALLBACK 4: CADASTRO INTERNO DE USUÁRIO
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


    # CALLBACK 5: ATUALIZAÇÃO DOS DADOS FILTRADOS
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

        # Cria uma cópia do DataFrame completo para filtragem
        dff_to_filter = df.copy()
        
        # Garante que a coluna de data no DataFrame esteja no formato datetime64[ns]
        # e normalizada para meia-noite, para uma comparação consistente apenas por data.
        dff_to_filter['Data_Apenas_norm'] = pd.to_datetime(dff_to_filter['Data_Apenas']).dt.normalize()

        # Converte start_date e end_date (que vêm como strings do DatePickerRange)
        # para objetos datetime64[ns] normalizados para meia-noite.
        if start_date:
            start_date_dt = pd.to_datetime(start_date).normalize()
        if end_date:
            end_date_dt = pd.to_datetime(end_date).normalize()

        # Aplica filtros sequencialmente usando a nova coluna de data normalizada
        if start_date and end_date:
            dff_to_filter = dff_to_filter[
                (dff_to_filter['Data_Apenas_norm'] >= start_date_dt) &
                (dff_to_filter['Data_Apenas_norm'] <= end_date_dt)
            ]
        
        if empresas:
            dff_to_filter = dff_to_filter[dff_to_filter['Empresa'].isin(empresas)]
        
        if destinos:
            dff_to_filter = dff_to_filter[dff_to_filter['Destino'].isin(destinos)]
        
        if materiais:
            dff_to_filter = dff_to_filter[dff_to_filter['Material'].isin(materiais)]
        
        # Retorna o DataFrame filtrado. A coluna temporária 'Data_Apenas_norm' não precisa
        # ser mantida no DataFrame final se não for usada para exibição.
        # O Pandas serializará 'Data_Apenas' (original) ou qualquer outra coluna de data corretamente.
        return dff_to_filter.to_json(date_format='iso', orient='split')


    # CALLBACK 6: LIMPAR FILTROS
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
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        
        return df.to_json(date_format='iso', orient='split'), \
               start_date, end_date, \
               [], [], []

    # CALLBACK 7: TOGGLE DA BARRA LATERAL (Agora não faz nada visualmente, só muda a classe)
    @app.callback(
        Output('dashboard-wrapper', 'className'),
        Output('sidebar-toggle-button', 'children'),
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

        if 'sidebar-minimized' in current_dashboard_class:
            new_class = current_dashboard_class.replace(' sidebar-minimized', '')
            button_icon = html.I(className="bi bi-list", style={"fontSize": "1.5rem"}) # CORRIGIDO: fontSize
        else:
            new_class = current_dashboard_class + ' sidebar-minimized'
            button_icon = html.I(className="bi bi-x-lg", style={"fontSize": "1.5rem"}) # CORRIGIDO: fontSize

        return new_class, button_icon

    # CALLBACK 8: VISIBILIDADE DO LINK DE GESTÃO DE USUÁRIOS E NOME DE USUÁRIO NA TOPBAR/HEADER
    @app.callback(
        Output('nav-link-user-management', 'style'), # Esconde/mostra o link de gestão de usuários
        Output('header-user-name', 'children'), # Adicionado Output para o nome de usuário no header
        Input('login-status-store', 'data'),
    )
    def update_user_management_link_and_info_and_header(login_status):
        """
        Controla a visibilidade do link 'Gestão de Usuários' com base no status de admin
        e atualiza o nome do usuário logado no cabeçalho.
        """
        if login_status and login_status.get('is_authenticated'):
            username = login_status.get('username', 'Usuário')
            
            user_display_html = html.Div(
                html.Span(
                    username.capitalize(),
                    className="d-none d-md-inline-block me-2"
                )
            )

            if login_status.get('is_admin'):
                return {'display': 'flex'}, user_display_html
            else:
                return {'display': 'none'}, user_display_html
        else:
            return {'display': 'none'}, ""