# components/tabs/analysis_tab.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import THEME_COLORS

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
    """
    Cria o layout completo para a aba 'Análise Geral',
    calculando KPIs e gerando gráficos a partir do DataFrame fornecido.
    """
    colors = THEME_COLORS[theme]

    # --- Lógica de cálculo de KPIs e geração de gráficos ---

    # Verifique se o dff não está vazio para evitar erros
    if dff.empty:
        return html.Div([
            create_page_header("Visão Geral da Produção", "Dashboards e KPIs de produção da frota."),
            dbc.Alert("Nenhum dado disponível para o período selecionado ou com os filtros aplicados.", color="info", className="m-4")
        ])

    # Exemplo de Cálculos de KPIs
    # Substitua 'Volume', 'Viagens' e 'Veiculo' pelas colunas corretas do seu DataFrame
    # Certifique-se de que essas colunas existem no seu 'dff'.
    total_volume = dff['Volume'].sum() if 'Volume' in dff.columns else 0
    total_trips = dff.shape[0] # Contagem de linhas como total de viagens
    frota_operando = dff['Veiculo'].nunique() if 'Veiculo' in dff.columns else 0 # Exemplo: Contar veículos únicos

    # Formatação dos KPIs
    volume_str = f"{total_volume:,.2f} m³".replace(",", "X").replace(".", ",").replace("X", ".") # Formato brasileiro
    trips_str = f"{int(total_trips):,}".replace(",", ".")
    frota_str = str(int(frota_operando))

    # Gráfico 1: Volume por Hora do Dia
    fig_volume_by_hour = go.Figure() # Inicializa com figura vazia para caso a condição não seja atendida
    if 'Data_Hora' in dff.columns and 'Volume' in dff.columns:
        df_volume_hora = dff.copy()
        # Garante que 'Data_Hora' é datetime antes de extrair a hora
        df_volume_hora['Data_Hora'] = pd.to_datetime(df_volume_hora['Data_Hora'])
        df_volume_hora['Hora_Apenas'] = df_volume_hora['Data_Hora'].dt.hour
        volume_por_hora = df_volume_hora.groupby('Hora_Apenas')['Volume'].sum().reset_index()
        
        # Ordena as horas para garantir que o gráfico seja exibido corretamente
        volume_por_hora = volume_por_hora.sort_values('Hora_Apenas')

        fig_volume_by_hour = px.bar(
            volume_por_hora,
            x='Hora_Apenas',
            y='Volume',
            title='Volume Total por Hora do Dia',
            labels={'Hora_Apenas': 'Hora do Dia', 'Volume': 'Volume (m³)'},
            color_discrete_sequence=[colors['primary']],
            template='plotly_dark' if theme == 'dark' else 'plotly_white'
        )
        fig_volume_by_hour.update_layout(
            plot_bgcolor=colors['card_bg'],
            paper_bgcolor=colors['card_bg'],
            font_color=colors['text'],
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig_volume_by_hour.update_traces(marker_color=colors['primary'])


    # Gráfico 2: Viagens por Material
    fig_trips_by_material = go.Figure() # Inicializa com figura vazia
    if 'Material' in dff.columns: # Verifique apenas 'Material', a contagem de linhas é sempre possível
        # Para viagens, contamos as linhas por material
        viagens_por_material = dff.groupby('Material').size().reset_index(name='Numero_Viagens')
        
        fig_trips_by_material = px.pie(
            viagens_por_material,
            values='Numero_Viagens',
            names='Material',
            title='Distribuição de Viagens por Material',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel # Uma paleta de cores para o gráfico de pizza
        )
        fig_trips_by_material.update_layout(
            plot_bgcolor=colors['card_bg'],
            paper_bgcolor=colors['card_bg'],
            font_color=colors['text'],
            margin=dict(l=20, r=20, t=40, b=20)
        )


    # Gráfico 3: Desempenho Semanal (Volume e Viagens ao longo da semana)
    fig_weekly_performance = go.Figure() # Inicializa com figura vazia
    if 'Data_Apenas' in dff.columns and 'Volume' in dff.columns: # 'Viagens' pode ser calculado pela contagem de linhas
        # Garante que 'Data_Apenas' é datetime antes de agrupar
        df_semanal = dff.copy()
        df_semanal['Data_Apenas'] = pd.to_datetime(df_semanal['Data_Apenas'])

        df_semanal_agg = df_semanal.groupby('Data_Apenas').agg(
            Total_Volume=('Volume', 'sum'),
            Total_Viagens=('Material', 'size') # Contar o número de entradas para 'Viagens'
        ).reset_index()
        
        # Certifique-se de que Data_Apenas é datetime para ordenação
        df_semanal_agg = df_semanal_agg.sort_values('Data_Apenas')

        fig_weekly_performance = px.line(
            df_semanal_agg,
            x='Data_Apenas',
            y=['Total_Volume', 'Total_Viagens'],
            title='Desempenho Diário: Volume e Viagens',
            labels={'Data_Apenas': 'Data', 'value': 'Valor', 'variable': 'Métrica'},
            color_discrete_map={'Total_Volume': colors['primary'], 'Total_Viagens': colors['secondary']},
            template='plotly_dark' if theme == 'dark' else 'plotly_white'
        )
        fig_weekly_performance.update_layout(
            plot_bgcolor=colors['card_bg'],
            paper_bgcolor=colors['card_bg'],
            font_color=colors['text'],
            xaxis_title=None,
            yaxis_title=None,
            legend_title_text='Métricas',
            margin=dict(l=20, r=20, t=40, b=20)
        )
        fig_weekly_performance.update_xaxes(showgrid=False)
        fig_weekly_performance.update_yaxes(gridcolor=colors['grid_line'])

    # --- Layout da aba com os dados reais ---
    return html.Div([
        create_page_header("Visão Geral da Produção", "Dashboards e KPIs de produção da frota."),
        dbc.Row([
            create_metric_card("Volume Total", volume_str, "Volume total produzido hoje"),
            create_metric_card("Viagens Realizadas", trips_str, "Total de viagens no dia"),
            create_metric_card("Frota Operando", frota_str, "Número de veículos ativos"),
        ], className="g-4 mb-4"),
        dbc.Row([
            dbc.Col(create_chart_card("Volume por Hora", "Distribuição do volume ao longo do dia", fig_volume_by_hour), lg=6, className="mb-4"),
            dbc.Col(create_chart_card("Viagens por Material", "Quantidade de viagens por tipo de material", fig_trips_by_material), lg=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(create_chart_card("Desempenho Diário", "Volume e viagens ao longo do período", fig_weekly_performance), lg=12, className="mb-4"),
        ])
    ])