# components/tabs/analysis_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from components.common_components import create_page_header, create_metric_card, create_chart_card
from components.kpis import create_kpi_layout
from config import THEME_COLORS
from components.kpis import create_kpi_layout
from logic.analysis_functions import (
    calculate_secondary_kpis,
    get_volume_by_weekday,
    get_volume_by_hour,
    get_top_5_by_column,
    create_figure_from_df
)

# --- Funções auxiliares para criar componentes reusáveis ---

def create_page_header(title, description):
    return html.Div([
        html.H1(title, className="app-header-title"),
        html.P(description, className="app-header-description mb-4")
    ])

def create_metric_card(title, value, description):
    return dbc.Col(dbc.Card([
        dbc.CardHeader(title, className="kpi-title"),
        dbc.CardBody(
            [
                html.H2(value, className="kpi-value"),
                html.P(description, className="metric-card-description")
            ]
        )
    ], className="kpi-card"), md=4, className="mb-4")

def create_chart_card(title, description, figure):
    return dbc.Card(
        dbc.CardBody([
            html.H5(title, className="chart-card-title"),
            html.P(description, className="chart-card-description"),
            dcc.Graph(figure=figure, config={'displayModeBar': False})
        ]),
        className="content-card"
    )

def create_analysis_tab_layout(dff, theme):
    """
    Cria o layout completo para a aba 'Visão Geral da Produção' com todas as novas análises.
    """
    
    if dff.empty:
        return dbc.Alert("Não há dados para os filtros selecionados.", color="info", className="m-4 text-center")

    # --- 1. Buscar todos os dados calculados ---
    secondary_kpis = calculate_secondary_kpis(dff)
    df_volume_weekday = get_volume_by_weekday(dff)
    df_volume_hour = get_volume_by_hour(dff)
    df_top_destinos = get_top_5_by_column(dff, 'Destino', 'Volume')
    df_top_veiculos = get_top_5_by_column(dff, 'Placa', 'Volume')

    # --- 2. Criar todas as figuras para os gráficos ---
    fig_volume_weekday = create_figure_from_df(df_volume_weekday, 'bar', 'Dia_Da_Semana', 'Volume', 'Volume por Dia da Semana')
    fig_volume_hour = create_figure_from_df(df_volume_hour, 'bar', 'Hora_Do_Dia', 'Volume', 'Volume por Hora do Dia')
    
    # Gráficos de barras horizontais para Top 5
    fig_top_destinos = create_figure_from_df(df_top_destinos, 'bar', 'Volume', 'Destino', 'Top 5 Destinos por Volume', orientation='h')
    if fig_top_destinos:
        fig_top_destinos.update_layout(yaxis={'categoryorder':'total ascending'})

    fig_top_veiculos = create_figure_from_df(df_top_veiculos, 'bar', 'Volume', 'Placa', 'Top 5 Veículos por Volume', orientation='h')
    if fig_top_veiculos:
        fig_top_veiculos.update_layout(yaxis={'categoryorder':'total ascending'})

    # --- 3. Montar o Layout da página ---
    layout = html.Div([
        create_page_header("Visão Geral da Produção", "Dashboards e KPIs de produção da frota."),
        
        # Linha dos KPIs principais (usando a função de kpis.py)
        create_kpi_layout(dff, theme),

        # Linha dos novos KPIs secundários
        dbc.Row([
            create_metric_card("Viagens 1º Turno", secondary_kpis['viagens_turno1'], "Das 06:00 às 17:59"),
            create_metric_card("Viagens 2º Turno", secondary_kpis['viagens_turno2'], "Das 18:00 às 05:59"),
            create_metric_card("Melhor Dia (Volume)", secondary_kpis['melhor_dia_data'], f"Volume: {secondary_kpis['melhor_dia_volume']}"),
            create_metric_card("Destino Mais Rentável", secondary_kpis['destino_rentavel'], "Baseado na receita total do período"),
        ], className="g-4 mb-4"),

        # Linha dos gráficos de análise temporal
        dbc.Row([
            dbc.Col(create_chart_card("Volume por Dia da Semana", "Performance ao longo da semana", fig_volume_weekday), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Volume por Hora do Dia", "Picos de produção durante o dia", fig_volume_hour), lg=6, className="mb-4"),
        ]),

        # Linha dos gráficos de Top 5
        dbc.Row([
            dbc.Col(create_chart_card("Top 5 Destinos", "Maiores volumes por destino", fig_top_destinos), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Top 5 Veículos", "Maiores volumes por placa", fig_top_veiculos), lg=6, className="mb-4"),
        ]),
    ])
    
    return layout