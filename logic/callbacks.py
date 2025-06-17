# logic/callbacks.py

# --- 1. IMPORTAÇÕES ---
from dash import Input, Output, State, html, dcc, exceptions, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO
from flask_login import login_user, logout_user, current_user
from datetime import datetime
import database
from components.header import TOPBAR_NAV_ITEMS
from components.common_components import create_page_header
from components.tabs.analysis_tab import create_analysis_tab_layout
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout
from components.tabs.user_management_tab import create_user_management_layout
from components.tabs.client_registration_tab import create_client_registration_layout
from components.tabs.pricing_registration_tab import create_pricing_registration_layout

# --- 2. FUNÇÃO DE REGISTRO DE CALLBACKS ---
def register_callbacks(app, df): # 'app' e 'df' são passados aqui

    # TODOS OS CALLBACKS ABAIXO DEVEM ESTAR DENTRO DESTA FUNÇÃO
    # E DEVEM ESTAR CORRETAMENTE INDENTADOS.

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


    # CALLBACK 2: RENDERIZADOR DE CONTEÚDO E TÍTULO (e controle de filtro)
    @app.callback(
        Output('page-content-container', 'children'),
        Output('filter-panel-wrapper', 'style'),
        Output('page-content-col', 'md'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data'),
        Input('filter-toggle-store', 'data'), # <<< NOVO INPUT
    )
    def render_page_content_and_title(pathname, jsonified_data, filter_toggle_state): # <<< NOVO ARGUMENTO
        # Lógica de autenticação
        if not current_user.is_authenticated:
            if pathname == "/logout":
                return (dcc.Location(pathname="/login", id="redirect-logout-not-auth"), {'display': 'none'}, 12)
            else:
                raise exceptions.PreventUpdate

        dff = pd.read_json(StringIO(jsonified_data), orient='split') if jsonified_data else df.copy()
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div()
        
        # Determine se o filtro deveria estar visível pelo pathname
        filter_visible_by_pathname = (pathname in ["/", "/matrix", "/efficiency"])
        
        # Determine o estado atual do filtro pelo botão de alternar
        is_hidden_by_toggle = filter_toggle_state.get('is_hidden', False)

        # Lógica FINAL para visibilidade e largura
        if filter_visible_by_pathname and not is_hidden_by_toggle:
            final_filter_style = {'display': 'block'}
            final_content_col_width = 9
        else:
            final_filter_style = {'display': 'none'}
            final_content_col_width = 12

        # Roteamento de conteúdo com base no pathname
        if pathname == "/":
            page_content = create_analysis_tab_layout(dff, 'dark')
        elif pathname == "/matrix":
            page_content = create_matrix_tab_layout(dff, 'dark')
        elif pathname == "/efficiency":
            page_content = create_efficiency_tab_layout(dff, 'dark')
        elif pathname == "/register-client":
            page_content = create_client_registration_layout(dff, 'dark')
        elif pathname == "/pricing":
            page_content = create_pricing_registration_layout(dff, 'dark')
        elif pathname == "/management/users":
            if not current_user.is_admin:
                return (dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4"), final_filter_style, final_content_col_width)
            page_content = create_user_management_layout()
        elif pathname in ["/management/equipment", "/settings"]:
            page_title_text = next((item["label"] for item in TOPBAR_NAV_ITEMS if item["href"] == pathname), "Página")
            page_content = html.Div([create_page_header(page_title_text, f"Funcionalidade em desenvolvimento."), dbc.Alert("Em breve.", color="info", className="m-4")])
        elif pathname == "/logout":
            logout_user()
            return (
                html.Div(
                    className="auth-container-background",
                    children=[
                        dbc.Card(
                            [
                                html.Div(html.Img(src="/assets/logo_fleetmaster.png", className="login-logo"), className="login-logo-container"),
                                html.Div(html.H2("Saindo...", className="text-center mb-4 logout-title"), className="mb-4"),
                                html.Div(dbc.Spinner(size="lg", color="primary", type="grow"), className="text-center mb-3"),
                                dcc.Location(id="redirect-logout", refresh=True),
                                dcc.Interval(id="logout-interval", interval=500, n_intervals=0, max_intervals=1)
                            ],
                            className="auth-card login-card-border"
                        )
                    ]
                ),
                {'display': 'none'}, # Esconde o filtro (fixo para logout)
                12 # Largura total (fixo para logout)
            )
        else:
            page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        
        return page_content, final_filter_style, final_content_col_width

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


    # NOVO CALLBACK: Para o cadastro de clientes
    @app.callback(
        Output('client-registration-output', 'children'),
        Output('destination-dropdown', 'options'), # Para atualizar a lista de destinos do dropdown
        Output('destination-dropdown', 'value'), # Para limpar o valor selecionado
        Output('destinations-without-client-list', 'children'), # Output para a lista de destinos sem cliente
        Input('register-client-button', 'n_clicks'),
        State('client-name-input', 'value'),
        State('destination-dropdown', 'value'),
        prevent_initial_call=True
    )
    def handle_client_registration(n_clicks, client_name, destination):
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate

        if not client_name or not destination:
            return (
                dbc.Alert("Preencha o nome do cliente e selecione um destino.", color="warning", duration=3000),
                no_update, # Opções do dropdown não mudam
                no_update, # Valor do dropdown não limpa
                no_update # Lista não muda
            )

        # Lógica de cálculo que será usada em AMBOS os retornos (sucesso e falha)
        unique_destinations_from_df = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
        registered_clients = database.get_all_clients()
        registered_destinations = {client['destination'] for client in registered_clients}
        
        destinations_without_client = [
            dest for dest in unique_destinations_from_df 
            if dest not in registered_destinations
        ]

        new_destinations_list_component = html.Div([
            dbc.ListGroup([
                dbc.ListGroupItem(dest, color="danger") for dest in destinations_without_client
            ]) if destinations_without_client else html.P("Todos os destinos têm clientes cadastrados ou não há destinos nos dados.")
        ])

        new_dropdown_options = [{'label': dest, 'value': dest} for dest in destinations_without_client]


        if database.add_client(client_name, destination):
            return (
                dbc.Alert(f"Cliente '{client_name}' para Destino '{destination}' cadastrado com sucesso!", color="success", duration=3000),
                new_dropdown_options,
                None,
                new_destinations_list_component
            )
        else:
            return (
                dbc.Alert(f"Falha ao cadastrar cliente. O destino '{destination}' pode já estar cadastrado.", color="danger", duration=3000),
                new_dropdown_options,
                destination,
                new_destinations_list_component
            )
        
        # NOVO CALLBACK: Para o cadastro de precificação - ADICIONADO AQUI
    @app.callback(
        Output('pricing-registration-output', 'children'), # 1
        Output('pricing-destination-dropdown', 'value'),   # 2
        Output('price-per-ton-input', 'value'),           # 3
        Output('start-date-picker', 'date'),              # 4
        Output('end-date-picker', 'date'),                # 5
        Output('registered-pricing-table', 'data'),       # 6
        Output('pricing-destination-dropdown', 'options'), # 7
        Input('register-price-button', 'n_clicks'),
        State('pricing-destination-dropdown', 'value'),
        State('price-per-ton-input', 'value'),
        State('start-date-picker', 'date'),
        State('end-date-picker', 'date'),
        prevent_initial_call=True
    )
    def handle_pricing_registration(n_clicks, destination, price_per_ton, start_date_str, end_date_str):
        # print(f"DEBUG: Callback de precificação acionado! n_clicks={n_clicks}") # Linha de debug opcional
        
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate

        # 1. Validação básica de campos
        if not all([destination, price_per_ton, start_date_str, end_date_str]):
            return (
                dbc.Alert("Preencha todos os campos para cadastrar o preço.", color="warning", duration=3000),
                no_update, no_update, no_update, no_update, no_update, no_update, no_update # <<< AGORA 7 no_update's
            )
        
        # 2. Conversão e validação de datas (formato 'YYYY-MM-DD' do DatePicker)
        try:
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return (
                dbc.Alert("Formato de data inválido. Use AAAA-MM-DD.", color="danger", duration=3000),
                no_update, no_update, no_update, no_update, no_update, no_update, no_update # <<< AGORA 7 no_update's
            )

        if start_date_obj > end_date_obj:
            return (
                dbc.Alert("A 'Data de Início' não pode ser posterior à 'Data Final'.", color="danger", duration=3000),
                no_update, no_update, no_update, no_update, no_update, no_update, no_update # <<< AGORA 7 no_update's
            )

        # 3. Tenta adicionar a precificação usando a função do database.py
        success = database.add_pricing(destination, price_per_ton, start_date_str, end_date_str)

        # 4. Recalcular e preparar dados para atualização dos Outputs (este bloco já estava correto)
        all_pricing = database.get_all_pricing()
        pricing_table_data = [dict(row) for row in all_pricing]
        for row in pricing_table_data:
            if 'price_per_ton' in row and pd.notnull(row['price_per_ton']):
                row['price_per_ton'] = f"{row['price_per_ton']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        unique_destinations_from_df = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
        new_dropdown_options_pricing = [{'label': dest, 'value': dest} for dest in unique_destinations_from_df]

        # 5. Retorno com base no sucesso ou falha do cadastro (estes blocos já estavam corretos na contagem)
        if success:
            return (
                dbc.Alert(f"Preço para '{destination}' ({start_date_str} a {end_date_str}) cadastrado com sucesso!", color="success", duration=3000),
                None, # Limpa o destino selecionado
                None, # Limpa o preço
                None, # Limpa a data de início
                None, # Limpa a data final
                pricing_table_data, # Atualiza a tabela
                new_dropdown_options_pricing # Atualiza as opções do dropdown
            )
        else:
            return (
                dbc.Alert(f"Falha ao cadastrar preço. Verifique sobreposições de período ou campos. (Destino: {destination})", color="danger", duration=5000),
                destination, # Mantém o destino selecionado
                price_per_ton, # Mantém o preço
                start_date_str, # Mantém a data de início
                end_date_str, # Mantém a data final
                pricing_table_data, # Atualiza a tabela (mesmo em caso de falha, para refletir o estado atual)
                new_dropdown_options_pricing # Atualiza as opções do dropdown
            )

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
        Output('navbar-collapse', 'is_open'), # Saída para o estado do Collapse
        [Input('navbar-toggler', 'n_clicks')], # Entrada do botão hamburguer
    )
    def toggle_navbar_collapse(n_clicks): # n_clicks é o único argumento agora
        print(f"DEBUG: toggle_navbar_collapse acionado. n_clicks: {n_clicks}")
        if n_clicks is None:
            # Se não houve cliques ainda, o menu deve estar fechado
            return False
        
        # O menu estará aberto se o número de cliques for ímpar, e fechado se for par
        return n_clicks % 2 == 1

    # CALLBACK 8: VISIBILIDADE DO LINK DE GESTÃO DE USUÁRIOS E NOME DE USUÁRIO NA TOPBAR/HEADER
    @app.callback(
        Output('nav-link-user-management', 'style'), # Esconde/mostra o link de gestão de usuários
        Output('header-user-name', 'children'), # Adicionado Output para o nome de usuário no header
        Output('nav-link-client-registration', 'style'), # ADICIONADO: Visibilidade do link de Cadastro de Clientes
        Input('login-status-store', 'data'),
    )
    def update_user_management_link_and_info_and_header(login_status):
        """
        Controla a visibilidade dos links 'Gestão de Usuários' e 'Cadastro de Clientes'
        com base no status de admin e atualiza o nome do usuário logado no cabeçalho.
        """
        if login_status and login_status.get('is_authenticated'):
            username = login_status.get('username', 'Usuário')
            
            user_display_html = html.Div(
                html.Span(
                    username.capitalize(),
                    className="d-none d-md-inline-block me-2"
                )
            )

            # Visibilidade do link de Gestão de Usuários (apenas para admin)
            user_management_style = {'display': 'flex'} if login_status.get('is_admin') else {'display': 'none'}
            
            # Visibilidade do link de Cadastro de Clientes (assumindo que qualquer usuário logado pode acessar)
            client_registration_style = {'display': 'flex'} # Visível para todos logados, ajuste se precisar de admin_only

            return user_management_style, user_display_html, client_registration_style
        else:
            # Se não logado, esconder ambos os links e limpar nome de usuário
            return {'display': 'none'}, "", {'display': 'none'}