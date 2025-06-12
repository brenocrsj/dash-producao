# logic/callbacks.py (Versão com Roteador de Conteúdo)

# --- 1. IMPORTAÇÕES DE BIBLIOTECAS EXTERNAS ---
from dash import Input, Output, html, exceptions
import pandas as pd
from io import StringIO
import dash_bootstrap_components as dbc

# --- 2. IMPORTAÇÕES DO NOSSO PROJETO ---
from components.sidebar import SIDEBAR_NAV_ITEMS
from components.tabs.analysis_tab import create_analysis_tab_layout
from components.tabs.matrix_tab import create_matrix_tab_layout
from components.tabs.efficiency_tab import create_efficiency_tab_layout


# --- 3. FUNÇÃO DE REGISTRO DE CALLBACKS ---
def register_callbacks(app, df):
    """Agrupa e registra todos os callbacks da aplicação."""
    
    # CALLBACK 1: FILTRAGEM DOS DADOS (RESTAURADO)
    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('empresa-dropdown', 'value'),
        Input('destino-dropdown', 'value'),
        Input('material-dropdown', 'value'),
    )
    def update_filtered_data(start_date, end_date, empresas, destinos, materiais):
        dff = df.copy()
        if start_date and end_date:
            dff = dff[(dff['Data_Apenas'] >= pd.to_datetime(start_date).date()) & (dff['Data_Apenas'] <= pd.to_datetime(end_date).date())]
        if empresas: dff = dff[dff['Empresa'].isin(empresas)]
        if destinos: dff = dff[dff['Destino'].isin(destinos)]
        if materiais: dff = dff[dff['Material'].isin(materiais)]
        return dff.to_json(date_format='iso', orient='split')

    # CALLBACK 2: LIMPAR FILTROS (RESTAURADO)
    @app.callback(
        Output('date-picker-range', 'start_date'),
        Output('date-picker-range', 'end_date'),
        Output('empresa-dropdown', 'value'),
        Output('destino-dropdown', 'value'),
        Output('material-dropdown', 'value'),
        Input('clear-filters-button', 'n_clicks')
    )
    def clear_all_filters(n_clicks):
        if n_clicks is None or n_clicks == 0:
            raise exceptions.PreventUpdate
        return (df['Data_Hora'].min().date(), df['Data_Hora'].max().date(), [], [], [])

    # CALLBACK 3: ATUALIZAR O TÍTULO DA PÁGINA (Mantido)
    @app.callback(
        Output('page-title', 'children'),
        Input('url', 'pathname')
    )
    def update_page_title(pathname):
        if pathname == "/": return "Análise Geral"
        for item in SIDEBAR_NAV_ITEMS:
            if item["href"] != "/" and pathname.startswith(item["href"]): return item["title"]
        return "Página não encontrada"
        
    # ==============================================================================
    # CALLBACK 4: O NOVO ROTEADOR DE CONTEÚDO!
    # Este callback decide qual página/dashboard mostrar com base na URL.
    # ==============================================================================
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
        Input('filtered-data-store', 'data')
    )
    def render_page_content(pathname, jsonified_data):
        if not jsonified_data:
            raise exceptions.PreventUpdate
            
        dff = pd.read_json(StringIO(jsonified_data), orient='split')
        dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
        dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
        dff['Dia_Da_Semana_Num'] = dff['Data_Hora'].dt.dayofweek
        
        # Lógica de roteamento
        if pathname == "/":
            return create_analysis_tab_layout(dff, theme='dark')
        elif pathname == "/matrix":
            return create_matrix_tab_layout(dff, theme='dark')
        elif pathname == "/efficiency":
            return create_efficiency_tab_layout(dff)
        # Se a URL não corresponder a nenhuma página, exibe uma mensagem de erro 404
        else:
            return dbc.Alert(
                [
                    html.H4("Erro 404: Página não encontrada", className="alert-heading"),
                    html.P(f"O caminho '{pathname}' não foi reconhecido. Por favor, utilize a navegação na barra lateral."),
                ],
                color="danger",
            )