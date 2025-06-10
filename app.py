import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import numpy as np
from io import StringIO # Importante para o futuro do pandas

# --- 1. FUNÇÕES AUXILIARES ---

def clean_numeric_column(series):
    """Converte uma coluna para numérico, tratando vírgulas e erros."""
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

def clean_text_column(series):
    """Limpa e padroniza uma coluna de texto."""
    return series.astype(str).str.strip().str.upper()

def load_and_prepare_data():
    """Carrega, pré-processa e une os dados das abas do Google Sheets."""
    try:
        # Links de exportação CSV para suas planilhas
        url_volume = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=0'
        url_frota = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=1061355856'
        url_precificacao = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=998298177'
        
        # Carregamento dos dados usando os links
        df_volume = pd.read_csv(url_volume)
        df_frota = pd.read_csv(url_frota)
        df_precificacao = pd.read_csv(url_precificacao)
        
        print("Dados carregados do Google Sheets com sucesso!")

        # Renomeação de colunas para padronização
        df_volume.rename(columns={'Coluna1': 'TAG'}, inplace=True, errors='ignore')
        df_frota.rename(columns={'PLACA': 'Placa'}, inplace=True, errors='ignore')
        df_precificacao.rename(columns={'Frente': 'Destino'}, inplace=True, errors='ignore')

        # Limpeza e padronização das colunas de texto
        for col in ['Destino', 'Material', 'Placa', 'TAG']:
            if col in df_volume.columns:
                df_volume[col] = clean_text_column(df_volume[col])
        if 'Placa' in df_frota.columns:
            df_frota['Placa'] = clean_text_column(df_frota['Placa'])
        if 'Destino' in df_precificacao.columns:
            df_precificacao['Destino'] = clean_text_column(df_precificacao['Destino'])

        # Processamento de datas e valores numéricos
        df_volume['Data_Hora'] = pd.to_datetime(
            df_volume['Data'].astype(str) + ' ' + df_volume['Hora'].astype(str),
            format='mixed', errors='coerce'
        )
        df_volume.dropna(subset=['Data_Hora'], inplace=True)
        df_volume['Data_Apenas'] = df_volume['Data_Hora'].dt.date
        df_volume['Hora_Do_Dia'] = df_volume['Data_Hora'].dt.hour
        df_volume['Volume'] = clean_numeric_column(df_volume['Volume'])

        # Junção dos DataFrames
        df_merged = pd.merge(df_volume, df_frota, on='Placa', how='left')
        df_final = pd.merge(df_merged, df_precificacao, on='Destino', how='left')

        # Limpeza das colunas pós-merge
        for col in ['Valor Bruto', 'Volume Máx']:
            if col in df_final.columns:
                df_final[col] = clean_numeric_column(df_final[col])
        for col in ['Empresa', 'Proprietario', 'Modelo', 'Tipo', 'STATUS', 'IDENTIFICAÇÃO', 'FROTA', 'CLIENTE']:
            if col in df_final.columns:
                df_final[col] = clean_text_column(df_final[col])

        # Cálculos de negócio
        if 'Volume' in df_final.columns and 'Valor Bruto' in df_final.columns:
            df_final['Valor Bruto Total'] = df_final['Volume'] * df_final['Valor Bruto']
        else:
            if 'Valor Bruto Total' not in df_final.columns:
                df_final['Valor Bruto Total'] = 0

        df_final['Turno'] = np.where((df_final['Hora_Do_Dia'] >= 6) & (df_final['Hora_Do_Dia'] < 18), '1º Turno', '2º Turno')
        df_final['Dia_Da_Semana_Num'] = pd.to_datetime(df_final['Data_Apenas']).dt.dayofweek
        dias_semana_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
        df_final['Dia_Da_Semana'] = df_final['Dia_Da_Semana_Num'].map(dias_semana_map)

        return df_final
        
    except Exception as e:
        print(f"Ocorreu um erro ao carregar os dados do Google Sheets: {e}")
        return None

def create_matrix_data(dff):
    """Cria o DataFrame formatado para a tabela matriz com subtotais e totais gerais."""
    if dff.empty:
        return pd.DataFrame()

    agg_spec = {
        'Volume': ['sum', 'min', 'mean', 'max'],
        'Placa': [('Nº Viagens', 'count')],
        'Turno': [
            ('Viagens 1º Turno', lambda x: (x == '1º Turno').sum()),
            ('Viagens 2º Turno', lambda x: (x == '2º Turno').sum())
        ]
    }
    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(agg_spec)
    grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]
    grouped.reset_index(inplace=True)

    agg_subtotal = {
        'Volume_sum': 'sum', 'Volume_min': 'min', 'Volume_max': 'max',
        'Placa_Nº Viagens': 'sum', 'Turno_Viagens 1º Turno': 'sum', 'Turno_Viagens 2º Turno': 'sum'
    }
    subtotals = grouped.groupby('Data_Apenas').agg(agg_subtotal).reset_index()
    
    frota_por_dia = dff.groupby('Data_Apenas')['TAG'].nunique().reset_index(name='Frota Total')
    subtotals = subtotals.merge(frota_por_dia, on='Data_Apenas')
    if not subtotals.empty and 'Placa_Nº Viagens' in subtotals.columns and (subtotals['Placa_Nº Viagens'] > 0).any():
        subtotals['Volume_mean'] = subtotals['Volume_sum'] / subtotals['Placa_Nº Viagens']
        subtotals['Viagens Média'] = subtotals['Placa_Nº Viagens'] / subtotals['Frota Total']
    else:
        subtotals['Volume_mean'] = 0
        subtotals['Viagens Média'] = 0

    subtotals['TAG'] = '--- TOTAL DIA ---'
    
    matrix_df = pd.concat([grouped, subtotals]).sort_values(by=['Data_Apenas', 'TAG'])
    
    matrix_df.rename(columns={
        'Data_Apenas': 'Data', 'Volume_sum': 'Volume Total', 'Volume_min': 'Volume Mín',
        'Volume_mean': 'Volume Médio', 'Volume_max': 'Volume Máximo',
        'Placa_Nº Viagens': 'Nº Viagens', 'Turno_Viagens 1º Turno': 'Viagens 1º Turno',
        'Turno_Viagens 2º Turno': 'Viagens 2º Turno',
    }, inplace=True)

    if not subtotals.empty:
        grand_total_calc = subtotals.sum(numeric_only=True)
        grand_total = pd.DataFrame([grand_total_calc])
        grand_total['Data'] = ''
        grand_total['TAG'] = '--- GRANDE TOTAL ---'
        grand_total['Frota Total'] = dff['TAG'].nunique()
        if grand_total['Frota Total'].iloc[0] > 0:
            grand_total['Viagens Média'] = grand_total['Placa_Nº Viagens'] / grand_total['Frota Total']
        
        grand_total.rename(columns={
            'Placa_Nº Viagens': 'Nº Viagens', 'Volume_sum': 'Volume Total', 'Volume_min': 'Volume Mín',
            'Volume_mean': 'Volume Médio', 'Volume_max': 'Volume Máximo', 
            'Turno_Viagens 1º Turno': 'Viagens 1º Turno', 'Turno_Viagens 2º Turno': 'Viagens 2º Turno'
        }, inplace=True)
        
        matrix_df = pd.concat([matrix_df, grand_total], ignore_index=True)
    
    matrix_df['Data'] = pd.to_datetime(matrix_df['Data'], errors='coerce').dt.strftime('%Y-%m-%d')
    matrix_df.loc[matrix_df['TAG'].isin(['--- TOTAL DIA ---', '--- GRANDE TOTAL ---']), 'Data'] = matrix_df['Data']
    matrix_df.loc[~matrix_df['TAG'].isin(['--- TOTAL DIA ---', '--- GRANDE TOTAL ---']), 'Data'] = ''

    return matrix_df

# --- 2. CARREGAMENTO INICIAL DOS DADOS ---
df = load_and_prepare_data()
if df is None or df.empty:
    print("FALHA AO CARREGAR DADOS. O dashboard não pode ser iniciado.")
    exit()

# --- 3. INICIALIZAÇÃO DO APP DASH ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 
server = app.server # Expor o servidor para o Gunicorn
app.title = "Análise Operacional de Produção"

# --- 4. LAYOUT DO DASHBOARD ---
app.layout = dbc.Container(fluid=True, className="app-container", children=[
    dcc.Store(id='filtered-data-store'),
    
    html.Div(className="app-header", children=[
        html.H1("Performance da Frota"),
        html.P("Monitoramento e Análise de Operações de Transporte"),
    ]),
    
    dbc.Card(className="filter-panel", body=True, children=[
        dbc.Row([
            dbc.Col(dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=df['Data_Apenas'].min(), max_date_allowed=df['Data_Apenas'].max(),
                start_date=df['Data_Apenas'].min(), end_date=df['Data_Apenas'].max(),
                display_format='DD/MM/YYYY', className="date-picker-style"
            ), width=12, lg=4, className="mb-3"),
            dbc.Col(dcc.Dropdown(
                id='empresa-dropdown', multi=True, placeholder='Filtrar por Empresa...',
                options=[{'label': i, 'value': i} for i in df['Empresa'].dropna().unique()]
            ), width=12, lg=2, className="mb-3"),
            dbc.Col(dcc.Dropdown(
                id='destino-dropdown', multi=True, placeholder='Filtrar por Destino...',
                options=[{'label': i, 'value': i} for i in df['Destino'].dropna().unique()]
            ), width=12, lg=3, className="mb-3"),
            dbc.Col(dcc.Dropdown(
                id='material-dropdown', multi=True, placeholder='Filtrar por Material...',
                options=[{'label': i, 'value': i} for i in df['Material'].dropna().unique()]
            ), width=12, lg=3, className="mb-3"),
        ]),
        dbc.Row([
            dbc.Col(dbc.Button("Limpar Todos os Filtros", id='clear-filters-button', color="primary", className="w-100"), 
                    width=12)
        ])
    ]),

    dbc.Row([
        dbc.Col(dbc.Card(className="kpi-card", children=[
            html.Div(className="kpi-content", children=[
                html.H2(id="kpi-volume-total", className="kpi-value"), html.P("Volume Total (t)", className="kpi-title")
            ]),
        ]), lg=3, md=6),
        dbc.Col(dbc.Card(className="kpi-card", children=[
            html.Div(className="kpi-content", children=[
                html.H2(id="kpi-valor-total", className="kpi-value"), html.P("Faturamento Total (R$)", className="kpi-title")
            ]),
        ]), lg=3, md=6),
        dbc.Col(dbc.Card(className="kpi-card", children=[
            html.Div(className="kpi-content", children=[
                html.H2(id="kpi-n-viagens", className="kpi-value"), html.P("Nº de Viagens", className="kpi-title")
            ]),
        ]), lg=3, md=6),
        dbc.Col(dbc.Card(className="kpi-card", children=[
            html.Div(className="kpi-content", children=[
                html.H2(id="kpi-frota-unica", className="kpi-value"), html.P("Veículos Únicos", className="kpi-title")
            ]),
        ]), lg=3, md=6),
    ], className="g-4 mb-4"),

    dcc.Tabs(id="tabs-main", value='tab-graphs', className="custom-tabs", children=[
        dcc.Tab(label='Dashboard Gráfico', value='tab-graphs', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(className="tab-content", children=[
                dbc.Row([dbc.Col(dbc.Card(dcc.Graph(id='grafico-volume-diario')), width=12)], className="g-4 mb-4 mt-2"),
                dbc.Row([dbc.Col(dbc.Card(dcc.Graph(id='grafico-viagens-dia')), width=12)], className="g-4 mb-4"),
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-volume-destino')), lg=6, md=12),
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-valor-bruto-empresa')), lg=6, md=12),
                ], className="g-4 mb-4"),
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-volume-material')), lg=6, md=12),
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-viagens-tag')), lg=6, md=12),
                ], className="g-4 mb-4"),
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-volume-hourly-distribution')), lg=6, md=12),
                    dbc.Col(dbc.Card(dcc.Graph(id='grafico-anual-comparison')), lg=6, md=12),
                ], className="g-4 mb-4"),
            ])
        ]),
        dcc.Tab(label='Análise Matricial', value='tab-matrix', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(className="tab-content", children=[
                dbc.Row([
                    dbc.Col(dbc.Card(className="kpi-card", children=[html.Div(className="kpi-content", children=[html.H2(id="kpi-matrix-dias", className="kpi-value"), html.P("Dias na Análise", className="kpi-title")])]), lg=4, md=6),
                    dbc.Col(dbc.Card(className="kpi-card", children=[html.Div(className="kpi-content", children=[html.H2(id="kpi-matrix-tags", className="kpi-value"), html.P("TAGs Únicas", className="kpi-title")])]), lg=4, md=6),
                    dbc.Col(dbc.Card(className="kpi-card", children=[html.Div(className="kpi-content", children=[html.H2(id="kpi-matrix-viagens", className="kpi-value"), html.P("Total de Viagens", className="kpi-title")])]), lg=4, md=12),
                ], className="g-4 mb-4 mt-2"),
                dbc.Row([
                    dbc.Col(dbc.Card(className="table-card", children=[
                        html.H4("Matriz de Desempenho Diário por TAG", className="table-title"),
                        dash_table.DataTable(
                            id='matrix-table', page_size=20, style_table={'overflowX': 'auto', 'minHeight': '50vh'},
                            fixed_rows={'headers': True}, style_header={'backgroundColor': '#2E3134', 'color': 'white', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': '#383b3e', 'color': 'white'},
                            style_data_conditional=[
                                {'if': {'filter_query': '{TAG} = "--- TOTAL DIA ---"'}, 'backgroundColor': '#4a4e52', 'fontWeight': 'bold'},
                                {'if': {'filter_query': '{TAG} = "--- GRANDE TOTAL ---"'}, 'backgroundColor': '#004C97', 'fontWeight': 'bold', 'color': '#FFD700'},
                            ]
                        )
                    ]), lg=8),
                    dbc.Col(dbc.Card(dcc.Graph(id='chart-matrix-top-tags')), lg=4),
                ], className="g-4 mb-4"),
            ])
        ]),
        dcc.Tab(label='Análise de Eficiência', value='tab-efficiency', className="custom-tab", selected_className="custom-tab--selected", children=[
            html.Div(className="tab-content", children=[
                dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-utilization-gauge')), lg=4, md=12, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-shift-performance')), lg=4, md=6, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-weekday-performance')), lg=4, md=6, className="mb-4"),
                ], className="mt-2"),
                dbc.Row([
                    dbc.Col(dbc.Card(className="table-card", children=[
                        html.H4("Ranking de Eficiência da Frota", className="table-title"),
                        dash_table.DataTable(
                            id='efficiency-ranking-table', page_size=10, style_table={'overflowX': 'auto'},
                            fixed_rows={'headers': True}, style_header={'backgroundColor': '#2E3134', 'color': 'white', 'fontWeight': 'bold'},
                            style_data={'backgroundColor': '#383b3e', 'color': 'white'},
                        )
                    ]), lg=6, md=12, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-load-efficiency')), lg=6, md=12, className="mb-4"),
                ]),
                 dbc.Row([
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-time-between-trips')), lg=6, md=12, className="mb-4"),
                    dbc.Col(dbc.Card(dcc.Graph(id='graph-profitability-analysis')), lg=6, md=12, className="mb-4"),
                ]),
            ])
        ]),
    ])
])


# --- 5. CALLBACKS ---
@app.callback(
    Output('filtered-data-store', 'data'),
    Input('date-picker-range', 'start_date'), Input('date-picker-range', 'end_date'),
    Input('empresa-dropdown', 'value'), Input('destino-dropdown', 'value'),
    Input('material-dropdown', 'value'),
)
def update_filtered_data(start_date, end_date, empresas, destinos, materiais):
    dff = df.copy()
    if start_date and end_date:
        dff = dff[(dff['Data_Apenas'] >= pd.to_datetime(start_date).date()) & (dff['Data_Apenas'] <= pd.to_datetime(end_date).date())]
    if empresas: dff = dff[dff['Empresa'].isin(empresas)]
    if destinos: dff = dff[dff['Destino'].isin(destinos)]
    if materiais: dff = dff[dff['Material'].isin(materiais)]
    return dff.to_json(date_format='iso', orient='split')

@app.callback(
    Output('date-picker-range', 'start_date'), Output('date-picker-range', 'end_date'),
    Output('empresa-dropdown', 'value'), Output('destino-dropdown', 'value'),
    Output('material-dropdown', 'value'),
    Input('clear-filters-button', 'n_clicks')
)
def clear_all_filters(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise dash.exceptions.PreventUpdate
    return df['Data_Apenas'].min(), df['Data_Apenas'].max(), [], [], []

def create_figure_from_df(fig_df, chart_type, x_col, y_col, title, color_sequence=None):
    fig = go.Figure()
    if fig_df.empty:
        fig.update_layout(title_text=f"{title}<br><sup>(Sem dados para o período)</sup>", title_x=0.5)
    elif chart_type == 'bar':
        fig = px.bar(fig_df, x=x_col, y=y_col, title=title, text_auto='.2s', color_discrete_sequence=color_sequence if color_sequence else ['#FFD700'])
    elif chart_type == 'line':
        fig = px.line(fig_df, x=x_col, y=y_col, title=title, markers=True, color_discrete_sequence=color_sequence if color_sequence else ['#FFD700'])
    
    fig.update_layout(
        template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f0f0f0'), margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

@app.callback(
    Output('kpi-volume-total', 'children'), Output('kpi-valor-total', 'children'),
    Output('kpi-n-viagens', 'children'), Output('kpi-frota-unica', 'children'),
    Output('grafico-volume-diario', 'figure'), Output('grafico-viagens-dia', 'figure'),
    Output('grafico-volume-destino', 'figure'), Output('grafico-valor-bruto-empresa', 'figure'),
    Output('grafico-volume-material', 'figure'), Output('grafico-viagens-tag', 'figure'),
    Output('grafico-anual-comparison', 'figure'), Output('grafico-volume-hourly-distribution', 'figure'),
    Output('matrix-table', 'data'), Output('matrix-table', 'columns'),
    Output('kpi-matrix-dias', 'children'), Output('kpi-matrix-tags', 'children'),
    Output('kpi-matrix-viagens', 'children'), Output('chart-matrix-top-tags', 'figure'),
    Output('graph-shift-performance', 'figure'), Output('graph-weekday-performance', 'figure'),
    Output('efficiency-ranking-table', 'data'), Output('efficiency-ranking-table', 'columns'),
    Output('graph-load-efficiency', 'figure'),
    Output('graph-utilization-gauge', 'figure'),
    Output('graph-time-between-trips', 'figure'),
    Output('graph-profitability-analysis', 'figure'),
    Input('filtered-data-store', 'data')
)
def update_visuals_and_kpis(jsonified_data):
    empty_fig = go.Figure().update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                          title_text="Sem dados", title_x=0.5, font_color='#bbbbbb', height=300)

    def return_empty():
        kpis = ["-"] * 4
        graphs_tab1 = [empty_fig] * 8
        matrix_items = [[], [], "-", "-", "-", empty_fig]
        efficiency_items = [empty_fig, empty_fig, [], [], empty_fig]
        new_efficiency_items = [empty_fig] * 3
        return tuple(kpis + graphs_tab1 + matrix_items + efficiency_items + new_efficiency_items)

    if not jsonified_data:
        return return_empty()

    # Usar StringIO para evitar o FutureWarning do Pandas
    dff = pd.read_json(StringIO(jsonified_data), orient='split')
    if dff.empty:
        return return_empty()

    dff['Data_Apenas'] = pd.to_datetime(dff['Data_Apenas']).dt.date
    dff['Data_Hora'] = pd.to_datetime(dff['Data_Hora'])
    
    kpi_volume_str = f"{dff['Volume'].sum():,.0f}"
    kpi_valor_str = f"R$ {dff['Valor Bruto Total'].sum():,.2f}"
    kpi_viagens_str = f"{len(dff):,}"
    kpi_frota_str = str(dff['TAG'].nunique())
    
    fig_diario = create_figure_from_df(dff.groupby(dff['Data_Hora'].dt.date)['Volume'].sum().reset_index(), 'line', 'Data_Hora', 'Volume', 'Volume Transportado por Dia')
    fig_viagens_dia = create_figure_from_df(dff.groupby(dff['Data_Hora'].dt.date).size().reset_index(name='Contagem'), 'line', 'Data_Hora', 'Contagem', 'Viagens por Dia', color_sequence=['#87CEEB'])
    fig_destino = create_figure_from_df(dff.groupby('Destino')['Volume'].sum().nlargest(15).reset_index(), 'bar', 'Destino', 'Volume', 'Top 15 Destinos por Volume')
    fig_valor_bruto = create_figure_from_df(dff.groupby('Empresa')['Valor Bruto Total'].sum().nlargest(15).reset_index(), 'bar', 'Empresa', 'Valor Bruto Total', 'Faturamento por Empresa', color_sequence=['#87CEEB'])
    fig_material = px.pie(dff.groupby('Material')['Volume'].sum().reset_index(), values='Volume', names='Material', title='Volume por Material', hole=0.4, color_discrete_sequence=px.colors.sequential.thermal)
    fig_material.update_layout(template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
    fig_viagens_tag = create_figure_from_df(dff.groupby('TAG').size().nlargest(15).reset_index(name='Contagem'), 'bar', 'TAG', 'Contagem', 'Top 15 TAGs por Nº de Viagens')
    dff['Ano'] = pd.to_datetime(dff['Data_Apenas']).dt.year
    fig_anual_comparison = create_figure_from_df(dff.groupby('Ano')['Volume'].sum().reset_index(), 'bar', 'Ano', 'Volume', 'Comparativo Anual de Volume')
    fig_anual_comparison.update_xaxes(type='category', title_text="Ano")
    dff['Hora_Do_Dia'] = dff['Data_Hora'].dt.hour
    fig_volume_hourly_distribution = create_figure_from_df(dff.groupby('Hora_Do_Dia')['Volume'].sum().reset_index(), 'bar', 'Hora_Do_Dia', 'Volume', 'Volume por Hora do Dia', color_sequence=['#004C97'])
    fig_volume_hourly_distribution.update_xaxes(tickmode='linear', dtick=1, title_text="Hora do Dia")

    matrix_df = create_matrix_data(dff.copy())
    
    matrix_detail_df = matrix_df[~matrix_df['TAG'].str.contains("---")].copy()
    if not matrix_detail_df.empty:
        matrix_detail_df['Nº Viagens'] = pd.to_numeric(matrix_detail_df['Nº Viagens'], errors='coerce')
        top_5_tags = matrix_detail_df.groupby('TAG')['Nº Viagens'].sum().nlargest(5).reset_index()
        fig_matrix_top_tags = create_figure_from_df(top_5_tags, 'bar', 'TAG', 'Nº Viagens', 'Top 5 TAGs na Análise')
    else:
        fig_matrix_top_tags = empty_fig

    for col in ['Volume Total', 'Volume Mín', 'Volume Médio', 'Volume Máximo', 'Viagens Média']:
        if col in matrix_df.columns:
            matrix_df[col] = matrix_df[col].apply(lambda x: f'{x:,.2f}' if pd.notnull(x) and x != '' else '')
    for col in ['Nº Viagens', 'Viagens 1º Turno', 'Viagens 2º Turno', 'Frota Total']:
        if col in matrix_df.columns:
            matrix_df[col] = matrix_df[col].apply(lambda x: f'{int(x):,}' if pd.notnull(x) and x != '' else '')

    cols_table = [{"name": i, "id": i} for i in matrix_df.columns]
    data_table = matrix_df.to_dict('records')
    kpi_matrix_dias_str, kpi_matrix_tags_str, kpi_matrix_viagens_str = str(matrix_df[matrix_df['TAG'] == '--- TOTAL DIA ---'].shape[0]), str(dff['TAG'].nunique()), f"{dff.shape[0]:,}"
    
    turno_summary = dff.groupby('Turno').agg(Volume=('Volume', 'sum'), Viagens=('Placa', 'count')).reset_index()
    fig_shift_performance = go.Figure(data=[go.Bar(name='Volume (t)', x=turno_summary['Turno'], y=turno_summary['Volume'], yaxis='y', offsetgroup=1), go.Bar(name='Nº Viagens', x=turno_summary['Turno'], y=turno_summary['Viagens'], yaxis='y2', offsetgroup=2)])
    fig_shift_performance.update_layout(title_text='Desempenho por Turno', template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(title='Volume Total (t)'), yaxis2=dict(title='Nº de Viagens', overlaying='y', side='right'), barmode='group', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_weekday_performance = create_figure_from_df(dff.groupby(['Dia_Da_Semana_Num', 'Dia_Da_Semana'])['Volume'].sum().reset_index().sort_values('Dia_Da_Semana_Num'), 'bar', 'Dia_Da_Semana', 'Volume', 'Volume por Dia da Semana', color_sequence=['#87CEEB'])
    tag_efficiency = dff.groupby('TAG').agg(Total_Viagens=('Placa', 'count'), Volume_Total=('Volume', 'sum')).reset_index()
    if not tag_efficiency.empty:
        tag_efficiency['Volume_Medio_Viagem'] = tag_efficiency['Volume_Total'] / tag_efficiency['Total_Viagens']
        tag_efficiency = tag_efficiency.sort_values(by='Total_Viagens', ascending=False).rename(columns={'TAG': 'Veículo (TAG)', 'Total_Viagens': 'Nº de Viagens', 'Volume_Total': 'Volume Total (t)', 'Volume_Medio_Viagem': 'Volume Médio/Viagem (t)'})
        for col in ['Volume Total (t)', 'Volume Médio/Viagem (t)']: tag_efficiency[col] = tag_efficiency[col].apply(lambda x: f"{x:,.2f}")
        tag_efficiency['Nº de Viagens'] = tag_efficiency['Nº de Viagens'].apply(lambda x: f"{x:,}")
    eff_cols = [{"name": i, "id": i} for i in tag_efficiency.columns]
    eff_data = tag_efficiency.to_dict('records')
    top_tags_list = tag_efficiency.head(10)['Veículo (TAG)'].tolist() if not tag_efficiency.empty else []
    dff_top_tags = dff[dff['TAG'].isin(top_tags_list)]
    fig_load_efficiency = px.box(dff_top_tags, x='TAG', y='Volume', color='TAG', title='Distribuição de Volume por Viagem (Top 10 Veículos)', labels={'TAG': 'Veículo', 'Volume': 'Volume da Carga (t)'}) if not dff_top_tags.empty else empty_fig
    fig_load_efficiency.update_layout(template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    fig_load_efficiency.update_xaxes(categoryorder='total descending')

    dff_utilizacao = dff[dff['Volume Máx'] > 0]
    fig_utilization_gauge = go.Figure(go.Indicator(mode="gauge+number", value=(dff_utilizacao['Volume'].sum()/dff_utilizacao['Volume Máx'].sum())*100, title={'text': "Utilização Média da Capacidade"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#FFD700"}, 'steps': [{'range': [0, 70], 'color': '#c0392b'}, {'range': [70, 90], 'color': '#f39c12'}, {'range': [90, 100], 'color': '#27ae60'}]}, number={'suffix': '%'})) if not dff_utilizacao.empty else empty_fig
    fig_utilization_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
    
    dff_sorted = dff.sort_values(by=['TAG', 'Data_Hora'])
    dff_sorted['Tempo_Horas'] = dff_sorted.groupby('TAG')['Data_Hora'].diff().dt.total_seconds() / 3600
    tempo_data = dff_sorted['Tempo_Horas'].dropna()
    tempo_data = tempo_data[tempo_data < 24]
    fig_time_between_trips = px.histogram(tempo_data, nbins=30, title='Distribuição do Tempo Entre Viagens (Horas)', labels={'value': 'Horas'}) if not tempo_data.empty else empty_fig
    fig_time_between_trips.update_layout(template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, bargap=0.1)
    fig_time_between_trips.update_traces(marker_color='#004C97')
    
    rentabilidade_df = dff.groupby('Material').agg(Faturamento_Total=('Valor Bruto Total', 'sum'), Volume_Total=('Volume', 'sum')).reset_index()
    rentabilidade_df = rentabilidade_df[rentabilidade_df['Volume_Total'] > 0]
    if not rentabilidade_df.empty:
        rentabilidade_df['Rentabilidade (R$/t)'] = rentabilidade_df['Faturamento_Total'] / rentabilidade_df['Volume_Total']
        fig_profitability = create_figure_from_df(rentabilidade_df.sort_values('Rentabilidade (R$/t)', ascending=False), 'bar', 'Material', 'Rentabilidade (R$/t)', 'Rentabilidade (R$/t) por Material')
    else:
        fig_profitability = empty_fig

    return (kpi_volume_str, kpi_valor_str, kpi_viagens_str, kpi_frota_str, fig_diario, fig_viagens_dia, fig_destino, fig_valor_bruto, fig_material, fig_viagens_tag, fig_anual_comparison, fig_volume_hourly_distribution, data_table, cols_table, kpi_matrix_dias_str, kpi_matrix_tags_str, kpi_matrix_viagens_str, fig_matrix_top_tags, fig_shift_performance, fig_weekday_performance, eff_data, eff_cols, fig_load_efficiency, fig_utilization_gauge, fig_time_between_trips, fig_profitability)

# --- 6. EXECUTAR O APP ---
if __name__ == '__main__':
    app.run(debug=False)