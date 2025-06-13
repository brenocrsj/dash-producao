# logic/callbacks.py

# --- 1. IMPORTAÇÕES ---
from dash import Input, Output, State, html, dcc, exceptions
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO
from flask_login import login_user, logout_user, current_user
from urllib.parse import parse_qs
import database
from components.sidebar import SIDEBAR_NAV_ITEMS
from components.tabs.analysis_tab import create_analysis_tab_layout, create_page_header
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout
from components.tabs.user_management_tab import create_user_management_layout


# --- 2. FUNÇÃO DE REGISTRO ---
def register_callbacks(app, df):
    """Agrupa e registra todos os callbacks da aplicação."""

    # CALLBACK 1: O "PORTEIRO" DE VISIBILIDADE
    @app.callback(
        Output('login-wrapper', 'style'),
        Output('dashboard-wrapper', 'style'),
        Input('url', 'pathname')
    )
    def master_visibility_router(pathname):
        if current_user.is_authenticated:
            # Se logado, esconde o login e mostra o dashboard
            return {'display': 'none'}, {'display': 'block'}
        # Se não logado, mostra o login e esconde o dashboard
        return {'display': 'flex'}, {'display': 'none'}

    # CALLBACK 2: RENDERIZADOR DE CONTEÚDO E TÍTULO
    @app.callback(
        Output('page-content-container', 'children'),
        Output('page-title', 'children'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content_and_title(pathname, jsonified_data):
        if not current_user.is_authenticated: raise exceptions.PreventUpdate
        dff = pd.read_json(StringIO(jsonified_data), orient='split') if jsonified_data else df.copy()
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora']); dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date; dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        page_title = "Página não encontrada"
        if pathname == "/": page_content, page_title = create_analysis_tab_layout(dff, 'dark'), "Análise Geral"
        elif pathname == "/matrix": page_content, page_title = create_matrix_tab_layout(dff, 'dark'), "Análise Matricial"
        elif pathname == "/efficiency": page_content, page_title = create_efficiency_tab_layout(dff, 'dark'), "Análise de Eficiência"
        elif pathname == "/management/users": page_content, page_title = create_user_management_layout(), "Gestão de Usuários"
        elif pathname in ["/management/equipment", "/settings"]:
            page_title = next((item["title"] for item in SIDEBAR_NAV_ITEMS if item["href"] == pathname), "Página")
            page_content = html.Div([create_page_header(page_title, f"Funcionalidade em desenvolvimento."), dbc.Alert("Em breve.", color="info", className="m-4")])
        elif pathname == "/logout": logout_user(); return dcc.Location(pathname="/login", id="redirect-logout"), "Saindo..."
        else: page_content = dbc.Alert("Erro 404: Página não encontrada.", color="danger", className="m-4")
        return page_content, page_title

    # CALLBACK 3: LÓGICA DE LOGIN
    @app.callback(
        Output('url', 'pathname'),
        Input('login-button', 'n_clicks'),
        State('username-input', 'value'),
        State('password-input', 'value'),
        prevent_initial_call=True
    )
    def handle_login(n_clicks, username, password):
        if not username or not password:
            print("Login falhou: campos vazios")
            return exceptions.no_update
        user = database.get_user_by_username(username)
        if user and database.check_password(user.password_hash, password):
            login_user(user)
            return "/"
        print(f"Login falhou para: {username}")
        return exceptions.no_update

    # CALLBACK 4: CADASTRO INTERNO DE USUÁRIO
    @app.callback(Output('user-management-message', 'children'), Input('create-user-button', 'n_clicks'), State('new-username-input', 'value'), State('new-password-input', 'value'), prevent_initial_call=True)
    def handle_internal_registration(n_clicks, username, password):
        if not username or not password: return dbc.Alert("Nome de usuário e senha são obrigatórios.", color="warning", duration=4000)
        if database.add_user(username, password): return dbc.Alert(f"Usuário '{username}' criado com sucesso!", color="success", duration=4000)
        return dbc.Alert(f"O nome de usuário '{username}' já existe.", color="danger", duration=4000)

    # CALLBACK 5: ATUALIZAÇÃO DOS DADOS FILTRADOS
    @app.callback(Output('filtered-data-store', 'data'), Input('date-picker-range', 'start_date'), Input('date-picker-range', 'end_date'), Input('empresa-dropdown', 'value'), Input('destino-dropdown', 'value'), Input('material-dropdown', 'value'))
    def update_filtered_data(start_date, end_date, empresas, destinos, materiais):
        if not current_user.is_authenticated: raise exceptions.PreventUpdate
        dff = df.copy()
        if start_date and end_date: dff = dff[(dff['Data_Apenas'] >= pd.to_datetime(start_date).date()) & (dff['Data_Apenas'] <= pd.to_datetime(end_date).date())]
        if empresas: dff = dff[dff['Empresa'].isin(empresas)]
        if destinos: dff = dff[dff['Destino'].isin(destinos)]
        if materiais: dff = dff[dff['Material'].isin(materiais)]
        return dff.to_json(date_format='iso', orient='split')

    # CALLBACK 6: LIMPAR FILTROS
    @app.callback(Output('filtered-data-store', 'data', allow_duplicate=True), Output('date-picker-range', 'start_date'), Output('date-picker-range', 'end_date'), Output('empresa-dropdown', 'value'), Output('destino-dropdown', 'value'), Output('material-dropdown', 'value'), Input('clear-filters-button', 'n_clicks'), prevent_initial_call=True)
    def clear_all_filters(n_clicks):
        start_date = df['Data_Apenas'].min()
        end_date = df['Data_Apenas'].max()
        return df.to_json(date_format='iso', orient='split'), start_date, end_date, [], [], []