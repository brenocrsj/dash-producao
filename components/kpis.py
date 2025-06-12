# components/kpis.py
from dash import html
import dash_bootstrap_components as dbc

def create_kpi_card(title, value_id):
    return dbc.Col(dbc.Card(className="kpi-card", children=[
        html.Div(className="kpi-content", children=[
            html.H2(id=value_id, className="kpi-value"), 
            html.P(title, className="kpi-title")
        ])
    ]), lg=3, md=6)

def create_kpi_layout():
    return dbc.Row([
        create_kpi_card("Volume Total (t)", "kpi-volume-total"),
        create_kpi_card("Faturamento Total (R$)", "kpi-valor-total"),
        create_kpi_card("Nº de Viagens", "kpi-n-viagens"),
        create_kpi_card("Veículos Únicos", "kpi-frota-unica"),
    ], className="g-4 mb-4")