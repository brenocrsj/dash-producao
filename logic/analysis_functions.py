# logic/analysis_functions.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_matrix_data(dff: pd.DataFrame) -> pd.DataFrame:
    """
    Cria o DataFrame formatado para a tabela da Análise Matricial,
    agrupando os dados por dia e por TAG.
    """
    # Se o DataFrame estiver vazio ou faltando colunas essenciais, retorna vazio
    if dff.empty or not all(col in dff.columns for col in ['Data_Apenas', 'TAG', 'Volume', 'Placa']):
        return pd.DataFrame()

    # <<< LÓGICA CORRETA DE AGRUPAMENTO >>>
    # Agrupa os dados por Data e TAG
    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(
        # Para cada grupo, soma o Volume
        Volume_Total=('Volume', 'sum'),
        # E conta o número de placas únicas para ter o número de viagens
        N_Viagens=('Placa', 'nunique')
    ).reset_index()

    # Retorna o DataFrame agrupado, que é a base da sua matriz
    return grouped


def create_figure_from_df(fig_df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, color_sequence=None) -> go.Figure:
    """
    Cria uma figura Plotly genérica a partir de um DataFrame.
    (Esta função permanece a mesma)
    """
    TEXT_COLOR = 'hsl(240, 10%, 95%)'
    PRIMARY_COLOR = 'hsl(220, 90%, 55%)'
    ACCENT_COLOR = 'hsl(45, 100%, 55%)'
    SECONDARY_COLOR = 'hsl(240, 10%, 15%)'
    BORDER_COLOR = 'hsl(240, 10%, 20%)'
    
    default_color_sequence = [PRIMARY_COLOR, 'hsl(220, 70%, 65%)', SECONDARY_COLOR]

    if color_sequence is None:
        color_sequence = default_color_sequence

    if chart_type == 'bar':
        fig = px.bar(fig_df, x=x_col, y=y_col, title=title, text_auto='.2s',
                     color_discrete_sequence=color_sequence)
    elif chart_type == 'line':
        fig = px.line(fig_df, x=x_col, y=y_col, title=title, markers=True,
                      color_discrete_sequence=color_sequence)
    else:
        fig = go.Figure()

    fig.update_layout(
        template="plotly_dark",
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=TEXT_COLOR, family='Inter, sans-serif'),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(showline=True, linecolor=ACCENT_COLOR, linewidth=2, gridcolor=BORDER_COLOR, zeroline=False),
        yaxis=dict(showline=True, linecolor=ACCENT_COLOR, linewidth=2, gridcolor=BORDER_COLOR, zeroline=False),
        hovermode="x unified"
    )
    return fig