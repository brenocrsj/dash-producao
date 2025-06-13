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
            return {'display': 'none'}, {'display': 'block'}, {'is_authenticated': True, 'is_admin': current_user.is_admin, 'username': current_user.username}
        return {'display': 'flex'}, {'display': 'none'}, {'is_authenticated': False, 'is_admin': False, 'username': None}


    # CALLBACK 2: RENDERIZADOR DE CONTEÚDO E TÍTULO
    @app.callback(
        Output('page-content-container', 'children'),
        # REMOVIDO: Output('page-title', 'children'), # <-- REMOVA ESTA LINHA
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content_and_title(pathname, jsonified_data):
        if not current_user.is_authenticated:
            if pathname == "/logout":
                return dcc.Location(pathname="/login", id="redirect-logout-not-auth"), "Redirecionando..."
            raise exceptions.PreventUpdate

        dff = pd.read_json(StringIO(jsonified_data), orient='split') if jsonified_data else df.copy()
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div()
        # page_title = "Página não encontrada" # Esta variável não é mais um Output, pode manter se usar internamente
        
        if pathname == "/":
            page_content = create_analysis_tab_layout(dff, 'dark')
            # page_title = "Análise Geral" # Não precisa ser Output, pode manter para referência
        elif pathname == "/matrix":
            page_content = create_matrix_tab_layout(dff, 'dark')
            # page_title = "Análise Matricial"
        elif pathname == "/efficiency":
            page_content = create_efficiency_tab_layout(dff, 'dark')
            # page_title = "Análise de Eficiência"
        elif pathname == "/management/users":
            if not current_user.is_admin:
                return dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4")
            page_content = create_user_management_layout()
            # page_title = "Gestão de Usuários"
        elif pathname in ["/management/equipment", "/settings"]:
            page_title_text = next((item["label"] for item in TOPBAR_NAV_ITEMS if item["href"] == pathname), "Página") # Usa o label
            page_content = html.Div([create_page_header(page_title_text, f"Funcionalidade em desenvolvimento."), dbc.Alert("Em breve.", color="info", className="m-4")])
            # page_title = page_title_text # Pode manter para referência
        elif pathname == "/logout":
            logout_user()
            page_content = html.Div([
                html.Div("Saindo...", className="logout-message"),
                dcc.Location(id="redirect-logout", refresh=True),
                dcc.Interval(id="logout-interval", interval=500, n_intervals=0, max_intervals=1)
            ], className="full-screen-logout-page")
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
            return "/", "" # Redireciona e limpa mensagem de erro
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

        dff = df.copy()
        
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
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        
        return df.to_json(date_format='iso', orient='split'), \
               start_date, end_date, \
               [], [], []

    # --- CALLBACK 7: TOGGLE DA BARRA LATERAL (Agora não faz nada visualmente, só muda a classe) ---
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
            button_icon = html.I(className="bi bi-list", style={"font-size": "1.5rem"})
        else:
            new_class = current_dashboard_class + ' sidebar-minimized'
            button_icon = html.I(className="bi bi-x-lg", style={"font-size": "1.5rem"})

        return new_class, button_icon

    # --- CALLBACK 8: VISIBILIDADE DO LINK DE GESTÃO DE USUÁRIOS E NOME DE USUÁRIO NA TOPBAR/HEADER ---
    @app.callback(
        Output('nav-link-user-management', 'style'),
        # REMOVIDO: Output('sidebar-user-info', 'children'), # Este ID não existe mais no layout
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