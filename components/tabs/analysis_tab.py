# components/tabs/analysis_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from config import THEME_COLORS # Importe THEME_COLORS de config

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

def create_analysis_tab_layout(dff, theme='dark'):
    """Cria o layout completo para a aba 'Análise Geral'."""
    colors = THEME_COLORS[theme]

    # Exemplo de dados para KPIs e gráficos (substitua pela sua lógica real)
    # df_kpis = ... # Seus dados processados para KPIs
    # fig_total_volume = ... # Seu gráfico de volume
    # fig_trips_by_hour = ... # Seu gráfico de viagens por hora

    # Conteúdo de exemplo
    return html.Div([
        create_page_header("Visão Geral da Produção", "Dashboards e KPIs de produção da frota."),
        dbc.Row([
            create_metric_card("Volume Total", "12.345 m³", "Volume total produzido hoje"),
            create_metric_card("Viagens Realizadas", "2.500", "Total de viagens no dia"),
            create_metric_card("Frota Operando", "50", "Número de veículos ativos"),
        ], className="g-4 mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Volume por Hora", "Distribuição do volume ao longo do dia", go.Figure()), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Viagens por Material", "Quantidade de viagens por tipo de material", go.Figure()), lg=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(create_chart_card("Desempenho Semanal", "Volume e viagens ao longo da semana", go.Figure()), lg=12, className="mb-4"),
        ])
    ])