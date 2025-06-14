# components/kpis.py
from dash import html
import dash_bootstrap_components as dbc

# Exemplo de como seus KPIs podem ser renderizados com cards
# Você pode ter uma função aqui para gerar um único KPI card, por exemplo.

def create_kpi_card(title, value, description):
    return dbc.Col(dbc.Card([
        dbc.CardHeader(title, className="kpi-title"),
        dbc.CardBody(
            [
                html.H2(value, className="kpi-value"),
                html.P(description, className="metric-card-description")
            ]
        )
    ], className="kpi-card"), md=4, className="mb-4") # Exemplo com md=4 para 3 cards por linha

# Se você tiver uma função que renderiza todos os KPIs, ajuste-a aqui.
# Por exemplo, se df_kpis for um DataFrame com os dados dos KPIs:
def render_kpis(df_kpis):
    return dbc.Row([
        create_kpi_card("Total Volume", f"{df_kpis.get('total_volume', 0):,.2f}", "Volume total na produção"),
        create_kpi_card("Avg. Viagens", f"{df_kpis.get('avg_trips', 0):.1f}", "Média de viagens por dia"),
        create_kpi_card("Frota Ativa", f"{df_kpis.get('active_fleet', 0)}", "Equipamentos ativos"),
    ], className="g-4 mb-4") # g-4 para espaçamento entre colunas