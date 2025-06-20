import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_secondary_kpis(dff: pd.DataFrame) -> dict:
    """Calcula uma variedade de KPIs secundários a partir do DataFrame."""
    if dff.empty:
        return {'viagens_turno1': 0, 'viagens_turno2': 0, 'melhor_dia_data': 'N/A', 'melhor_dia_volume': 0, 'destino_rentavel': 'N/A'}

    viagens_turno1 = dff[dff['Turno'] == '1º Turno'].shape[0]
    viagens_turno2 = dff[dff['Turno'] == '2º Turno'].shape[0]

    volume_por_dia = dff.groupby('Data_Apenas')['Volume'].sum()
    if not volume_por_dia.empty:
        melhor_dia_data = volume_por_dia.idxmax().strftime('%d/%m/%Y')
        melhor_dia_volume = volume_por_dia.max()
    else:
        melhor_dia_data, melhor_dia_volume = 'N/A', 0

    if 'Valor Bruto Total' in dff.columns:
        receita_por_destino = dff.groupby('Destino')['Valor Bruto Total'].sum()
        destino_rentavel = receita_por_destino.idxmax() if not receita_por_destino.empty else 'N/A'
    else:
        destino_rentavel = 'N/A'

    return {
        'viagens_turno1': f"{viagens_turno1:,}".replace(",", "."), 'viagens_turno2': f"{viagens_turno2:,}".replace(",", "."),
        'melhor_dia_data': melhor_dia_data, 'melhor_dia_volume': f"{(melhor_dia_volume / 1000):,.2f} t".replace(",", "X").replace(".", ",").replace("X", "."),
        'destino_rentavel': destino_rentavel
    }

def get_volume_by_weekday(dff: pd.DataFrame) -> pd.DataFrame:
    """Agrupa o volume por dia da semana."""
    if dff.empty or 'Dia_Da_Semana_Num' not in dff.columns: return pd.DataFrame()
    volume_por_dia = dff.groupby('Dia_Da_Semana_Num')['Volume'].sum().reset_index()
    dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    volume_por_dia['Dia_Da_Semana'] = pd.Categorical(volume_por_dia['Dia_Da_Semana_Num'].map(lambda x: dias[x]), categories=dias, ordered=True)
    return volume_por_dia.sort_values('Dia_Da_Semana_Num')

def get_volume_by_hour(dff: pd.DataFrame) -> pd.DataFrame:
    """Agrupa o volume por hora do dia."""
    if dff.empty or 'Hora_Do_Dia' not in dff.columns: return pd.DataFrame()
    return dff.groupby('Hora_Do_Dia')['Volume'].sum().reset_index()

def get_top_5_by_column(dff: pd.DataFrame, column: str, value_col: str) -> pd.DataFrame:
    """Retorna o Top 5 de uma coluna com base na soma de outra."""
    if dff.empty or column not in dff.columns or value_col not in dff.columns: return pd.DataFrame()
    return dff.groupby(column)[value_col].sum().nlargest(5).reset_index()

def create_matrix_data(dff: pd.DataFrame) -> pd.DataFrame:
    """Cria o DataFrame formatado para a tabela da Análise Matricial."""
    if dff.empty or not all(col in dff.columns for col in ['Data_Apenas', 'TAG', 'Volume', 'Placa']):
        print("AVISO em create_matrix_data: DataFrame vazio ou faltando colunas essenciais.")
        return pd.DataFrame()
    
    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(
        Volume_Total=('Volume', 'sum'),
        N_Viagens=('Placa', 'nunique')
    ).reset_index()
    return grouped

def create_figure_from_df(fig_df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, orientation='v', color_sequence=None) -> go.Figure:
    """
    Cria uma figura Plotly genérica com a paleta de cores VERDE.
    """
    if fig_df.empty:
        return go.Figure().update_layout(
            title_text=f"{title}<br><sup>(Sem dados para exibir)</sup>",
            title_x=0.5,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='white',
            font_color='black'
        )

    # <<< A CORREÇÃO ESTÁ AQUI, NA DEFINIÇÃO DA PALETA DE CORES >>>
    GREEN_PRIMARY = '#02971f'             # Seu verde principal
    GREEN_LIGHT = '#03c228'               # Um tom de verde mais claro para variações
    TEXT_COLOR_ON_WHITE_BG = '#111827'    # Cor do texto para o fundo branco (quase preto)
    GRID_COLOR_ON_WHITE_BG = '#e5e7eb'    # Cor das linhas de grade (cinza claro)
    TITLE_COLOR_ON_TRANSPARENT_BG = 'hsl(240, 10%, 95%)' # Cor do título (quase branco)

    
    # A sequência de cores agora começa com o verde
    default_color_sequence = [GREEN_PRIMARY, GREEN_LIGHT, '#0a9325', '#34d399']

    if color_sequence is None:
        color_sequence = default_color_sequence

    # Criação da figura
    if chart_type == 'bar':
        fig = px.bar(fig_df, x=x_col, y=y_col, title=title, text_auto='.2s',
                     color_discrete_sequence=color_sequence, orientation=orientation)
    elif chart_type == 'line':
        fig = px.line(fig_df, x=x_col, y=y_col, title=title, markers=True,
                      color_discrete_sequence=color_sequence)
    else:
        fig = go.Figure()

    # Layout do gráfico atualizado
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        font=dict(color=TEXT_COLOR_ON_WHITE_BG, family='Inter, sans-serif'),
        
        # Agora a variável existe e pode ser usada
        title_font=dict(color=TITLE_COLOR_ON_TRANSPARENT_BG),
        
        margin=dict(l=40, r=20, t=60, b=40),
        xaxis=dict(showline=True, linecolor=GRID_COLOR_ON_WHITE_BG, gridcolor=GRID_COLOR_ON_WHITE_BG),
        yaxis=dict(showline=False, gridcolor=GRID_COLOR_ON_WHITE_BG),
        hovermode="x unified",
        showlegend=False
    )
    
    fig.update_traces(marker_color=GREEN_PRIMARY, marker_line_width=0)
    
    return fig