# components/common_components.py
import dash_bootstrap_components as dbc
from dash import dcc, html

def create_page_header(title, subtitle):
    """Cria um cabeçalho de página padrão e estilizado."""
    return html.Div([
        html.H1(title, className="app-header-title"),
        html.P(subtitle, className="app-header-description")
    ], className="mb-5 text-center")

def create_metric_card(title, value, description=""):
    """Cria um card de KPI reutilizável e estilizado."""
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(html.H5(title, className="kpi-card-title")),
                dbc.CardBody(
                    [
                        html.P(value, className="kpi-card-value"),
                        html.P(description, className="kpi-card-description")
                    ]
                )
            ],
            className="kpi-card"
        ),
        xs=12, sm=6, md=4, className="mb-4"
    )

def create_chart_card(title, description, figure):
    """Cria um card de conteúdo para envolver um gráfico."""
    return dbc.Card(
        [
            dbc.CardHeader(html.H4(title, className="chart-card-title")),
            dbc.CardBody([
                html.P(description, className="chart-card-description mb-3"),
                dcc.Graph(figure=figure, config={'displayModeBar': False})
            ])
        ],
        className="content-card"
    )