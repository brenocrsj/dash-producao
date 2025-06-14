# components/tabs/matrix_tab.py
import dash_bootstrap_components as dbc
from dash import dcc, html
import dash_table
import plotly.graph_objects as go
import pandas as pd
from logic.data_processing import create_matrix_data, create_figure_from_df
from config import THEME_COLORS
from components.tabs.analysis_tab import create_page_header, create_metric_card, create_chart_card


def create_matrix_tab_layout(dff, theme='dark'):
    """Cria o layout completo para a aba 'Análise Matricial'."""
    if dff.empty:
        return dbc.Alert("Não há dados para os filtros selecionados.", color="info", className="m-4 text-center")

    colors = THEME_COLORS[theme]
    matrix_df = create_matrix_data(dff.copy()) # matrix_df contém 'N_Viagens'
    
    # --- NOVO FLUXO DE MANIPULAÇÃO DA COLUNA DE VIAGENS ---
    # 1. Garante que 'N_Viagens' seja numérico e renomeia para 'Nº Viagens' no matrix_df principal.
    if 'N_Viagens' in matrix_df.columns:
        matrix_df['N_Viagens'] = pd.to_numeric(matrix_df['N_Viagens'], errors='coerce')
        matrix_df.rename(columns={'N_Viagens': 'Nº Viagens'}, inplace=True) # Renomeia no DataFrame principal
    else:
        # Se 'N_Viagens' não existe, crie 'Nº Viagens' com zeros para evitar KeyError posterior
        matrix_df['Nº Viagens'] = 0
    # --- FIM NOVO FLUXO ---

    # matrix_detail_df é um subconjunto filtrado de matrix_df.
    # Agora, matrix_detail_df já deve conter 'Nº Viagens' se matrix_df o fez.
    matrix_detail_df = matrix_df[~matrix_df['TAG'].str.contains("---")].copy()
    
    # Gráfico Top 5 TAGs
    if not matrix_detail_df.empty and 'Nº Viagens' in matrix_detail_df.columns: # Verificação explícita da coluna
        top_5_tags = matrix_detail_df.groupby('TAG')['Nº Viagens'].sum().nlargest(5).reset_index()
        fig_matrix_top_tags = create_figure_from_df(top_5_tags, 'bar', 'TAG', 'Nº Viagens', 'Top 5 TAGs na Análise')
        fig_matrix_top_tags.update_layout(font=dict(color=colors['foreground']), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_matrix_top_tags.update_traces(marker_color=colors['accent'])
    else:
        fig_matrix_top_tags = go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_text="Sem dados ou coluna 'Nº Viagens' ausente para Top 5", title_x=0.5, font_color=colors['foreground'], height=300)

    # Formatação das colunas para exibição na tabela (usa matrix_df que agora já tem 'Nº Viagens')
    for col in ['Volume Total', 'Volume Mín', 'Volume Médio', 'Volume Máximo', 'Viagens Média']:
        if col in matrix_df.columns: matrix_df[col] = matrix_df[col].apply(lambda x: f'{x:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".") if pd.notnull(x) and x != '' else '')
    for col in ['Nº Viagens', 'Viagens 1º Turno', 'Viagens 2º Turno', 'Frota Total']: # 'Nº Viagens' já está presente aqui
        if col in matrix_df.columns: matrix_df[col] = matrix_df[col].apply(lambda x: f'{int(x):,}' if pd.notnull(x) and x != '' else '')

    cols_table = [{"name": i, "id": i} for i in matrix_df.columns]
    data_table = matrix_df.to_dict('records')

    layout = html.Div([
        create_page_header("Análise Matricial", "Detalhes da produção por TAG e Data."), # Uso de create_page_header
        dbc.Row([
            # Verificação para evitar erro se '--- TOTAL DIA ---' não existir ou for vazio
            create_metric_card("Dias na Análise", str(matrix_df[matrix_df['TAG'] == '--- TOTAL DIA ---'].shape[0]) if not matrix_df[matrix_df['TAG'] == '--- TOTAL DIA ---'].empty else '0', "Período selecionado"),
            create_metric_card("TAGs Únicas", str(dff['TAG'].nunique()), "Veículos únicos na análise"),
            create_metric_card("Total de Viagens", f"{dff.shape[0]:,}", "Viagens totais na análise"),
        ], className="g-4 mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card(className="table-card", children=[
                html.H4("Matriz de Desempenho Diário por TAG", className="chart-card-title mb-3"),
                dash_table.DataTable(
                    id='matrix-datatable',
                    columns=cols_table,
                    data=data_table, page_size=20,
                    fixed_rows={'headers': True},
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '8px',
                        'backgroundColor': 'hsl(var(--card))',
                        'color': 'hsl(var(--foreground))',
                        'border': '1px solid hsl(var(--border))'
                    },
                    style_header={
                        'backgroundColor': 'hsl(var(--secondary))',
                        'color': 'hsl(var(--secondary-foreground))',
                        'fontWeight': 'bold',
                        'border': '1px solid hsl(var(--border))'
                    },
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'},
                            'backgroundColor': 'hsl(var(--background), 0.5)',
                        },
                        {'if': {'filter_query': '{TAG} = "--- TOTAL DIA ---"'}, 'fontWeight': 'bold'},
                        {'if': {'filter_query': '{TAG} = "--- GRANDE TOTAL ---"'}, 'fontWeight': 'bold', 'backgroundColor': 'hsl(var(--primary))', 'color': 'hsl(var(--primary-foreground))'},
                    ]
                )
            ]), lg=8, className="mb-4"),
            dbc.Col(create_chart_card("Top 5 TAGs", "Veículos com mais viagens no período", fig_matrix_top_tags), lg=4, className="mb-4"),
        ]),
    ])
    return layout