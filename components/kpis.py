import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

def create_kpi_layout(df, theme):
    """Cria a seção de KPIs com o novo layout inspirado na imagem."""
    
    if df.empty:
        return dbc.Row([
            dbc.Col(dbc.Alert("Não há dados disponíveis para os filtros selecionados.", color="info"))
        ])
        
    # --- Cálculos dos KPIs ---
    
    # Cálculo do Volume em Toneladas
    total_volume_tons = (df['Volume'].sum() / 1000) if 'Volume' in df.columns else 0
    formatted_volume = f"{total_volume_tons:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Outros cálculos
    total_revenue = df['Valor Bruto Total'].sum() if 'Valor Bruto Total' in df.columns else 0
    formatted_revenue = f"R$ {total_revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    total_trips = df['Placa'].nunique() if 'Placa' in df.columns else 0
    formatted_trips = f"{total_trips:,}".replace(",", ".")
    
    avg_ticket = (total_revenue / total_trips) if total_trips > 0 else 0
    formatted_avg_ticket = f"R$ {avg_ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Lista de KPIs para criar os cards
    kpis = [
        {"id": "kpi-total-volume", "title": "Volume Total (t)", "value": formatted_volume, "icon": "bi bi-database-fill-add"},
        {"id": "kpi-total-revenue", "title": "Receita Total", "value": formatted_revenue, "icon": "bi bi-currency-dollar"},
        {"id": "kpi-total-trips", "title": "Total de Viagens", "value": formatted_trips, "icon": "bi bi-truck"},
        {"id": "kpi-avg-ticket", "title": "Ticket Médio", "value": formatted_avg_ticket, "icon": "bi bi-receipt-cutoff"},
    ]
    
    # <<< NOVA ESTRUTURA PARA OS CARDS >>>
    kpi_cards = []
    for kpi in kpis:
        card = dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    className="d-flex align-items-center p-3", # Container flexível principal
                    children=[
                        # Div para o ícone
                        html.Div(
                            html.I(className=f"{kpi['icon']} kpi-icon"),
                            className="kpi-icon-container"
                        ),
                        # Div para os textos (título e valor)
                        html.Div([
                            html.H6(kpi["title"], className="kpi-title"),
                            html.H4(kpi["value"], className="kpi-value", id=kpi["id"]),
                        ], className="kpi-text-container")
                    ]
                ),
                className="kpi-card",
            ),
            lg=3, md=6, sm=12, className="mb-4" # Responsividade dos cards
        )
        kpi_cards.append(card)
    
    return dbc.Row(kpi_cards)