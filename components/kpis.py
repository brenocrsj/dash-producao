import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

def create_kpi_layout(df, theme):
    """Cria a seção de KPIs (Key Performance Indicators) do dashboard."""
    
    if df.empty:
        return dbc.Row([
            dbc.Col(dbc.Alert("Não há dados disponíveis para os filtros selecionados.", color="info"))
        ])
        
    # --- Cálculos dos KPIs ---

    # <<< CORREÇÃO 2: Soma a coluna 'Volume' e divide por 1000 para ter o valor em TONELADAS >>>
    total_volume_tons = (df['Volume'].sum() / 1000) if 'Volume' in df.columns else 0
    # Formata o número para o padrão brasileiro com 2 casas decimais
    formatted_volume = f"{total_volume_tons:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Cálculos dos outros KPIs
    total_revenue = df['Valor Bruto Total'].sum() if 'Valor Bruto Total' in df.columns else 0
    formatted_revenue = f"R$ {total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    total_trips = df['Placa'].nunique() if 'Placa' in df.columns else 0
    formatted_trips = f"{total_trips:,}".replace(",", ".")
    
    avg_ticket = (total_revenue / total_trips) if total_trips > 0 else 0
    formatted_avg_ticket = f"R$ {avg_ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Lista de KPIs para criar os cards
    kpis = [
        # Usa a nova variável formatada no card de Volume
        {"id": "kpi-total-volume", "title": "Volume Total (t)", "value": formatted_volume, "icon": "bi bi-database-fill-add"},
        {"id": "kpi-total-revenue", "title": "Receita Total", "value": formatted_revenue, "icon": "bi bi-currency-dollar"},
        {"id": "kpi-total-trips", "title": "Total de Viagens", "value": formatted_trips, "icon": "bi bi-truck"},
        {"id": "kpi-avg-ticket", "title": "Ticket Médio", "value": formatted_avg_ticket, "icon": "bi bi-receipt-cutoff"},
    ]
    
    # Cria os cards de KPI dinamicamente
    kpi_cards = [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H6(kpi["title"], className="kpi-title"),
                    html.Div([
                        html.I(className=f"{kpi['icon']} kpi-icon"),
                        html.Span(kpi["value"], className="kpi-value", id=kpi["id"]),
                    ], className="d-flex align-items-center"),
                ]),
                className="kpi-card",
            ),
            md=3
        )
        for kpi in kpis
    ]
    
    return dbc.Row(kpi_cards, className="mb-4")