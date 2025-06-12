# components/tabs/matrix_tab.py
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import pandas as pd
from logic.data_processing import create_matrix_data, create_figure_from_df
from .analysis_tab import THEME_COLORS, create_metric_card, create_chart_card 
from config import THEME_COLORS # <-- MUDANÇA
from .analysis_tab import create_metric_card, create_chart_card

def create_matrix_tab_layout(dff, theme='dark'):
    """Cria o layout completo para a aba 'Análise Matricial'."""
    if dff.empty:
        return dbc.Alert("Não há dados para os filtros selecionados.", color="info", className="m-4 text-center")

    colors = THEME_COLORS[theme]
    matrix_df = create_matrix_data(dff.copy())
    
    # Gráfico Top 5 TAGs
    matrix_detail_df = matrix_df[~matrix_df['TAG'].str.contains("---")].copy()
    if not matrix_detail_df.empty:
        matrix_detail_df['Nº Viagens'] = pd.to_numeric(matrix_detail_df['Nº Viagens'], errors='coerce')
        top_5_tags = matrix_detail_df.groupby('TAG')['Nº Viagens'].sum().nlargest(5).reset_index()
        fig_matrix_top_tags = create_figure_from_df(top_5_tags, 'bar', 'TAG', 'Nº Viagens', 'Top 5 TAGs na Análise')
        fig_matrix_top_tags.update_layout(font=dict(color=colors['foreground']), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_matrix_top_tags.update_traces(marker_color=colors['accent'])
    else:
        fig_matrix_top_tags = go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_text="Sem dados", title_x=0.5, font_color=colors['foreground'], height=300)

    # Formatação das colunas para exibição na tabela
    for col in ['Volume Total', 'Volume Mín', 'Volume Médio', 'Volume Máximo', 'Viagens Média']:
        if col in matrix_df.columns: matrix_df[col] = matrix_df[col].apply(lambda x: f'{x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) and x != '' else '')
    for col in ['Nº Viagens', 'Viagens 1º Turno', 'Viagens 2º Turno', 'Frota Total']:
        if col in matrix_df.columns: matrix_df[col] = matrix_df[col].apply(lambda x: f'{int(x):,}' if pd.notnull(x) and x != '' else '')

    cols_table = [{"name": i, "id": i} for i in matrix_df.columns]
    data_table = matrix_df.to_dict('records')

    layout = html.Div([
        dbc.Row([
            create_metric_card("Dias na Análise", str(matrix_df[matrix_df['TAG'] == '--- TOTAL DIA ---'].shape[0]), "Período selecionado"),
            create_metric_card("TAGs Únicas", str(dff['TAG'].nunique()), "Veículos únicos na análise"),
            create_metric_card("Total de Viagens", f"{dff.shape[0]:,}", "Viagens totais na análise"),
        ], className="g-4 mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(className="table-card", children=[
                html.H4("Matriz de Desempenho Diário por TAG", className="chart-card-title mb-3"),
                dash_table.DataTable(
                    id='matrix-datatable',
                    data=data_table, columns=cols_table, page_size=20,
                    fixed_rows={'headers': True},
                    style_data_conditional=[
                        {'if': {'filter_query': '{TAG} = "--- TOTAL DIA ---"'}, 'fontWeight': 'bold'},
                        {'if': {'filter_query': '{TAG} = "--- GRANDE TOTAL ---"'}, 'fontWeight': 'bold', 'backgroundColor': 'hsl(var(--primary))', 'color': 'hsl(var(--primary-foreground))'},
                    ]
                )
            ]), lg=8, className="mb-4"),
            dbc.Col(create_chart_card("Top 5 TAGs", "Veículos com mais viagens no período", fig_matrix_top_tags), lg=4, className="mb-4"),
        ]),
    ])
    return layout