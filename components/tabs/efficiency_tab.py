# components/tabs/efficiency_tab.py
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from config import THEME_COLORS
from .analysis_tab import create_page_header, create_chart_card

def create_efficiency_tab_layout(dff, theme='dark'):
    """Cria o layout completo para a aba 'Análise de Eficiência'."""
    if dff.empty:
        return dbc.Alert("Não há dados para os filtros selecionados.", color="info", className="m-4 text-center")

    colors = THEME_COLORS[theme]
    
    # Gráfico de Desempenho por Turno
    turno_summary = dff.groupby('Turno').agg(Volume=('Volume', 'sum'), Viagens=('Placa', 'count')).reset_index()
    fig_shift_performance = go.Figure()
    if not turno_summary.empty:
        fig_shift_performance.add_trace(go.Bar(name='Volume (t)', x=turno_summary['Turno'], y=turno_summary['Volume'], marker_color=colors['primary']))
        fig_shift_performance.add_trace(go.Bar(name='Nº Viagens', x=turno_summary['Turno'], y=turno_summary['Viagens'], marker_color=colors['accent']))
    
    fig_shift_performance.update_layout(title_text=None, barmode='group', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # Atualiza o layout de todos os gráficos para o tema
    for fig in [fig_shift_performance]:
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color=colors['foreground']), margin=dict(t=10, b=10, l=10, r=10))

    layout = html.Div([
        create_page_header("Análise de Eficiência", "Comparativos de performance da frota."),
        dbc.Row([
            dbc.Col(create_chart_card("Desempenho por Turno", "Volume e viagens por turno.", fig_shift_performance), lg=6, className="mb-4"),
            # Outros gráficos de eficiência podem ser adicionados aqui
        ]),
    ])
    return layout