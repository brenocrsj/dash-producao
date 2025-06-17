# logic/callbacks.py (VERSÃO FINAL COMPLETA E CORRIGIDA)

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
def register_callbacks(app, df):
    """Registra todos os callbacks da aplicação."""

    # CALLBACK 1: ROTEADOR DE VISIBILIDADE (LOGIN vs DASHBOARD)
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


    # CALLBACK 2: RENDERIZADOR DE CONTEÚDO E LAYOUT (SEU "SUPER CALLBACK" CORRIGIDO)
    @app.callback(
        Output('page-content-container', 'children'),
        Output('filter-col', 'className'),
        Output('page-content-col', 'md'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data'),
        Input('filter-toggle-store', 'data')
    )
    def render_page_content_and_layout(pathname, jsonified_data, filter_toggle_state):
        if not current_user.is_authenticated:
            if pathname == "/logout":
                return dcc.Location(pathname="/login", id="redirect-logout-not-auth"), "d-none", 12
            raise exceptions.PreventUpdate

        # --- Parte A: Lógica de Layout ---
        is_page_with_filters = pathname in ["/", "/matrix", "/efficiency"]
        is_hidden_by_toggle = filter_toggle_state.get('is_hidden', False)

        if is_page_with_filters and not is_hidden_by_toggle:
            filter_col_class = "mb-4 d-flex justify-content-center align-items-start"
            content_col_md = 9
        else:
            filter_col_class = "d-none"
            content_col_md = 12

        # --- Parte B: Lógica de Conteúdo ---
        dff = pd.read_json(StringIO(jsonified_data), orient='split') if jsonified_data else df.copy()
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_content = html.Div()

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
                return dbc.Alert("Acesso negado: Você não tem permissão para esta página.", color="danger", className="m-4"), "d-none", 12
            page_content = create_user_management_layout()
        elif pathname in ["/management/equipment", "/settings"]:
            page_title_text = next((item["label"] for item in TOPBAR_NAV_ITEMS if item["href"] == pathname), "Página")
            page_content = html.Div([create_page_header(page_title_text, f"Funcionalidade em desenvolvimento."), dbc.Alert("Em breve.", color="info", className="m-4")])
        elif pathname == "/logout":
            logout_user()
            return dcc.Location(pathname="/login", id="redirect-logout"), "d-none", 12
        else:
            page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        
        return page_content, filter_col_class, content_col_md

    # CALLBACK 3: ATUALIZADOR DO BOTÃO E ESTADO DO FILTRO
    @app.callback(
        Output('filter-toggle-store', 'data'),
        Output('sidebar-toggle-button', 'children'),
        Input('sidebar-toggle-button', 'n_clicks'),
        State('filter-toggle-store', 'data'),
        prevent_initial_call=True
    )
    def update_filter_toggle_button_state(n_clicks, store_data):
        new_is_hidden = not store_data.get('is_hidden', False)
        if new_is_hidden:
            button_icon = html.I(className="bi bi-filter-circle")
        else:
            button_icon = html.I(className="bi bi-filter-circle-fill")
        return {'is_hidden': new_is_hidden}, button_icon

    # CALLBACK 4: LÓGICA DE LOGIN
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
        if not username or not password:
            return no_update, dbc.Alert("Preencha todos os campos.", color="warning", duration=3000)
        user = database.get_user_by_username(username)
        remember = True if remember_me_value and 1 in remember_me_value else False
        if user and database.check_password(user.password_hash, password):
            login_user(user, remember=remember)
            return "/", ""
        else:
            return no_update, dbc.Alert("Nome de usuário ou senha inválidos.", color="danger", duration=3000)

    # CALLBACK 5: CADASTRO INTERNO DE USUÁRIO
    @app.callback(
        Output('user-management-message', 'children'),
        Input('create-user-button', 'n_clicks'),
        State('new-username-input', 'value'),
        State('new-password-input', 'value'),
        prevent_initial_call=True
    )
    def handle_internal_registration(n_clicks, username, password):
        if not username or not password:
            return dbc.Alert("Nome de usuário e senha são obrigatórios.", color="warning", duration=4000)
        if database.add_user(username, password):
            return dbc.Alert(f"Usuário '{username}' criado com sucesso!", color="success", duration=4000)
        return dbc.Alert(f"O nome de usuário '{username}' já existe.", color="danger", duration=4000)

    # CALLBACK 6: CADASTRO DE CLIENTES
    @app.callback(
        Output('client-registration-output', 'children'),
        Output('destination-dropdown', 'options'),
        Output('destination-dropdown', 'value'),
        Output('destinations-without-client-list', 'children'),
        Input('register-client-button', 'n_clicks'),
        State('client-name-input', 'value'),
        State('destination-dropdown', 'value'),
        prevent_initial_call=True
    )
    def handle_client_registration(n_clicks, client_name, destination):
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate
        if not client_name or not destination:
            return dbc.Alert("Preencha o nome do cliente e selecione um destino.", color="warning", duration=3000), no_update, no_update, no_update
        
        unique_destinations_from_df = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
        registered_clients = database.get_all_clients()
        registered_destinations = {client['destination'] for client in registered_clients}
        destinations_without_client = [dest for dest in unique_destinations_from_df if dest not in registered_destinations]
        
        new_destinations_list_component = html.Div([dbc.ListGroup([dbc.ListGroupItem(dest, color="danger") for dest in destinations_without_client]) if destinations_without_client else html.P("Todos os destinos têm clientes cadastrados.")])
        new_dropdown_options = [{'label': dest, 'value': dest} for dest in destinations_without_client]
        
        if database.add_client(client_name, destination):
            return dbc.Alert(f"Cliente '{client_name}' para Destino '{destination}' cadastrado!", color="success", duration=3000), new_dropdown_options, None, new_destinations_list_component
        else:
            return dbc.Alert(f"Falha. O destino '{destination}' pode já estar cadastrado.", color="danger", duration=3000), new_dropdown_options, destination, new_destinations_list_component

    # CALLBACK 7: CADASTRO DE PRECIFICAÇÃO
    @app.callback(
        Output('pricing-registration-output', 'children'),
        Output('pricing-destination-dropdown', 'value'),
        Output('price-per-ton-input', 'value'),
        Output('start-date-picker', 'date'),
        Output('end-date-picker', 'date'),
        Output('registered-pricing-table', 'data'),
        Output('pricing-destination-dropdown', 'options'),
        Input('register-price-button', 'n_clicks'),
        State('pricing-destination-dropdown', 'value'),
        State('price-per-ton-input', 'value'),
        State('start-date-picker', 'date'),
        State('end-date-picker', 'date'),
        prevent_initial_call=True
    )
    def handle_pricing_registration(n_clicks, destination, price_per_ton, start_date_str, end_date_str):
        if not current_user.is_authenticated:
            raise exceptions.PreventUpdate
        if not all([destination, price_per_ton, start_date_str, end_date_str]):
            return dbc.Alert("Preencha todos os campos.", color="warning", duration=3000), no_update, no_update, no_update, no_update, no_update, no_update
        try:
            start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return dbc.Alert("Formato de data inválido.", color="danger", duration=3000), no_update, no_update, no_update, no_update, no_update, no_update
        if start_date_obj > end_date_obj:
            return dbc.Alert("A 'Data de Início' não pode ser posterior à 'Data Final'.", color="danger", duration=3000), no_update, no_update, no_update, no_update, no_update, no_update
        
        success = database.add_pricing(destination, price_per_ton, start_date_str, end_date_str)
        
        all_pricing = database.get_all_pricing()
        pricing_table_data = [dict(row) for row in all_pricing]
        for row in pricing_table_data:
            if 'price_per_ton' in row and pd.notnull(row['price_per_ton']):
                row['price_per_ton'] = f"{row['price_per_ton']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        unique_destinations_from_df = sorted(df['Destino'].dropna().unique()) if 'Destino' in df.columns else []
        new_dropdown_options_pricing = [{'label': dest, 'value': dest} for dest in unique_destinations_from_df]
        
        if success:
            return dbc.Alert(f"Preço para '{destination}' cadastrado!", color="success", duration=3000), None, None, None, None, pricing_table_data, new_dropdown_options_pricing
        else:
            return dbc.Alert(f"Falha. Verifique sobreposições de período.", color="danger", duration=5000), destination, price_per_ton, start_date_str, end_date_str, pricing_table_data, new_dropdown_options_pricing

    # CALLBACK 8: LIMPAR FILTROS
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
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        return df.to_json(date_format='iso', orient='split'), start_date, end_date, [], [], []

    # CALLBACK 9: TOGGLE DO MENU HAMBÚRGUER
    @app.callback(
        Output('navbar-collapse', 'is_open'),
        Input('navbar-toggler', 'n_clicks'),
        State('navbar-collapse', 'is_open'),
        prevent_initial_call=True
    )
    def toggle_navbar_collapse(n, is_open):
        return not is_open

    # CALLBACK 10: VISIBILIDADE DOS LINKS RESTRITOS E NOME DO USUÁRIO
    @app.callback(
        Output('nav-link-user-management', 'style'),
        Output('header-user-name', 'children'),
        Output('nav-link-client-registration', 'style'),
        Input('login-status-store', 'data'),
    )
    def update_user_management_link_and_info_and_header(login_status):
        if login_status and login_status.get('is_authenticated'):
            username = login_status.get('username', 'Usuário')
            user_display_html = html.Div(html.Span(username.capitalize(), className="d-none d-md-inline-block me-2"))
            user_management_style = {'display': 'flex'} if login_status.get('is_admin') else {'display': 'none'}
            client_registration_style = {'display': 'flex'}
            return user_management_style, user_display_html, client_registration_style
        else:
            return {'display': 'none'}, "", {'display': 'none'}