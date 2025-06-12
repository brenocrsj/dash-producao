# components/tabs/analysis_tab.py (Versão Corrigida)

import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
from config import THEME_COLORS #

# ==============================================================================
# CORREÇÃO: Dicionário de cores para o Python/Plotly entender.
# ==============================================================================
THEME_COLORS = {
    'light': {
        'foreground': 'hsl(220, 10%, 25%)',
        'primary': 'hsl(210, 85%, 55%)',
        'accent': 'hsl(30, 90%, 58%)',
        'chart_1': 'hsl(210, 85%, 55%)',
        'chart_2': 'hsl(30, 90%, 58%)',
        'chart_3': 'hsl(150, 70%, 45%)',
        'chart_4': 'hsl(260, 70%, 65%)',
        'chart_5': 'hsl(190, 70%, 50%)',
    },
    'dark': {
        'foreground': 'hsl(220, 15%, 95%)',
        'primary': 'hsl(210, 85%, 65%)',
        'accent': 'hsl(30, 90%, 68%)',
        'chart_1': 'hsl(210, 85%, 65%)',
        'chart_2': 'hsl(30, 90%, 68%)',
        'chart_3': 'hsl(150, 70%, 55%)',
        'chart_4': 'hsl(260, 70%, 75%)',
        'chart_5': 'hsl(190, 70%, 60%)',
    }
}


# --- Funções de Componentes Reutilizáveis (sem alterações) ---

def create_page_header(title, description):
    return html.Div([
        html.H1(title, className="app-header-title"),
        html.P(description, className="app-header-description")
    ], className="app-header")

def create_metric_card(title, value, description, trend=None):
    children = [
        html.P(title, className="kpi-title"),
        html.Div([html.H2(value, className="kpi-value")]),
        html.P(description, className="metric-card-description"),
    ]
    if trend:
        trend_class = "metric-card-trend-positive" if trend.startswith('+') else "metric-card-trend-negative"
        children.append(html.P(trend, className=f"metric-card-trend {trend_class}"))
    return dbc.Col(dbc.Card(children, body=True, className="kpi-card"), lg=4, md=6)

def create_chart_card(title, description, figure):
    return dbc.Card([
        dbc.CardHeader([
            html.H3(title, className="chart-card-title"),
            html.P(description, className="chart-card-description"),
        ]),
        dbc.CardBody(dcc.Graph(
            figure=figure,
            config={'displayModeBar': False}
        ), className="p-0")
    ], className="content-card")

# --- Função Principal de Layout da Aba (com a correção) ---

def create_analysis_tab_layout(dff, theme='dark'): # Adicionamos o parâmetro 'theme'
    """
    Cria o layout completo para a aba 'Análise Geral', usando os dados e o tema.
    """
    if dff.empty:
        return dbc.Alert("Não há dados para os filtros selecionados.", color="info", className="m-4 text-center")
    
    # Seleciona o dicionário de cores correto com base no tema
    colors = THEME_COLORS[theme]
    
    # --- 1. Geração dos Gráficos ---
    
    daily_volume_df = dff.groupby(dff['Data_Hora'].dt.date)['Volume'].sum().reset_index()
    fig_daily_volume = px.line(
        daily_volume_df, x='Data_Hora', y='Volume', markers=True,
        labels={'Data_Hora': 'Data', 'Volume': 'Volume (t)'}
    )

    weekday_map = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'}
    trips_per_day_df = dff.groupby(dff['Dia_Da_Semana_Num']).size().reset_index(name='Viagens')
    trips_per_day_df['Dia'] = trips_per_day_df['Dia_Da_Semana_Num'].map(weekday_map)
    fig_trips_per_day = px.bar(
        trips_per_day_df.sort_values('Dia_Da_Semana_Num'), x='Dia', y='Viagens',
        labels={'Dia': 'Dia da Semana', 'Viagens': 'Nº de Viagens'}
    )

    destination_volume_df = dff.groupby('Destino')['Volume'].sum().nlargest(5).reset_index()
    fig_destination_pie = px.pie(
        destination_volume_df, names='Destino', values='Volume', hole=0.4,
        labels={'Destino': 'Destino', 'Volume': 'Volume (t)'}
    )

    material_volume_df = dff.groupby('Material')['Volume'].sum().nlargest(5).reset_index()
    fig_material_pie = px.pie(
        material_volume_df, names='Material', values='Volume', hole=0.4,
        labels={'Material': 'Material', 'Volume': 'Volume (t)'}
    )

    # --- CORREÇÃO: Usando as cores do dicionário Python ---
    for fig in [fig_daily_volume, fig_trips_per_day, fig_destination_pie, fig_material_pie]:
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=colors['foreground']), # <-- USA A COR DO DICIONÁRIO
            showlegend=False, 
            margin=dict(t=10, b=10, l=10, r=10)
        )
    
    fig_daily_volume.update_traces(line_color=colors['primary'])
    fig_trips_per_day.update_traces(marker_color=colors['accent'])
    chart_colors = [colors[f'chart_{i+1}'] for i in range(5)]
    fig_destination_pie.update_traces(marker_colors=chart_colors)
    fig_material_pie.update_traces(marker_colors=chart_colors)
    
    
    # --- 2. Montagem do Layout da Página (sem alterações) ---
    
    layout = html.Div([
        create_page_header("Análise Geral", "Visão geral das métricas e performance da frota."),
        dbc.Row([
            create_metric_card("Volume Total Transportado", f"{dff['Volume'].sum():,.0f} t".replace(",", "."), "Volume total no período selecionado", "+2.5%"),
            create_metric_card("Nº de Viagens", f"{len(dff):,}".replace(",", "."), "Total de viagens no período", "-1.2%"),
            create_metric_card("Veículos Únicos", str(dff['TAG'].nunique()), "Frota única em operação no período"),
        ], className="g-4 mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Volume Transportado por Dia", "Volume total transportado nos últimos dias.", fig_daily_volume), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Viagens por Dia da Semana", "Distribuição de viagens ao longo da semana.", fig_trips_per_day), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Volume por Destino", "Principais destinos por volume transportado.", fig_destination_pie), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Volume por Material", "Distribuição do volume por tipo de material.", fig_material_pie), lg=6, className="mb-4"),
        ]),
    ])
    
    return layout