import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from logic.analysis_functions import create_matrix_data # <<< IMPORTAÇÃO CORRIGIDA

def create_matrix_tab_layout(dff, theme='dark'):
    """Cria o layout completo para a aba 'Análise Matricial'."""
    
    # Verifica se o DataFrame de entrada está vazio
    if dff.empty:
        return dbc.Alert("Não há dados para exibir com os filtros selecionados.", color="info", className="m-4")

    # Chama a função de análise para criar os dados da matriz
    matrix_df = create_matrix_data(dff)

    # Verifica se o resultado da análise está vazio
    if matrix_df.empty:
        return dbc.Alert("Não foi possível gerar a matriz com os dados disponíveis.", color="warning", className="m-4")

    # Define as colunas e os dados para a DataTable
    cols_table = [{"name": i, "id": i} for i in matrix_df.columns]
    data_table = matrix_df.to_dict('records')

    # Retorna o layout final da aba
    layout = html.Div([
        dbc.Card(className="table-card p-4", children=[
            html.H4("Matriz de Desempenho Diário", className="chart-card-title mb-3"),
            dash_table.DataTable(
                id='matrix-datatable',
                columns=cols_table,
                data=data_table,
                page_size=25,
                sort_action="native",
                filter_action="native",
                style_table={'overflowX': 'auto', 'minWidth': '100%'},
                style_cell={'textAlign': 'left', 'padding': '8px', 'backgroundColor': 'transparent'},
                style_header={'fontWeight': 'bold'},
            )
        ])
    ])
    
    return layout