import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_matrix_data(dff: pd.DataFrame) -> pd.DataFrame:
    """Cria o DataFrame formatado para a tabela da Análise Matricial."""
    if dff.empty or not all(col in dff.columns for col in ['Data_Apenas', 'TAG', 'Volume', 'Placa']):
        return pd.DataFrame()

    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(
        Volume_Total=('Volume', 'sum'),
        N_Viagens=('Placa', 'nunique')
    ).reset_index()
    return grouped

def create_figure_from_df(fig_df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, color_sequence=None) -> go.Figure:
    """Cria uma figura Plotly genérica a partir de um DataFrame."""
    TEXT_COLOR = 'hsl(240, 10%, 95%)'
    PRIMARY_COLOR = 'hsl(220, 90%, 55%)'
    ACCENT_COLOR = 'hsl(45, 100%, 55%)'
    BORDER_COLOR = 'hsl(240, 10%, 20%)'
    
    default_color_sequence = [PRIMARY_COLOR, 'hsl(220, 70%, 65%)', 'hsl(240, 10%, 15%)']
    if color_sequence is None:
        color_sequence = default_color_sequence

    if chart_type == 'bar':
        fig = px.bar(fig_df, x=x_col, y=y_col, title=title, text_auto='.2s', color_discrete_sequence=color_sequence)
    elif chart_type == 'line':
        fig = px.line(fig_df, x=x_col, y=y_col, title=title, markers=True, color_discrete_sequence=color_sequence)
    else:
        fig = go.Figure()

    fig.update_layout(
        title_x=0.5,
        paper_bgcolor='rgba(0,0,0,0)', # Fundo do papel (fora do gráfico) continua transparente
        plot_bgcolor='white',          # Fundo da área de plotagem (o gráfico) agora é BRANCO
        
        # Ajusta a fonte para ser legível no fundo branco
        font=dict(
            color='black', # Cor da fonte dos eixos e números agora é PRETA
            family='Inter, sans-serif'
        ),
        
        # Ajusta o título para ser legível
        title_font=dict(
            color='hsl(var(--foreground))' # Título do gráfico continua com a cor principal do tema
        ),
        
        margin=dict(l=40, r=40, t=80, b=40),
        
        # Ajusta os eixos para o fundo branco
        xaxis=dict(
            showline=True,
            linecolor='lightgrey', # Linha do eixo cinza claro
            gridcolor='lightgrey', # Linhas de grade cinza claro
            zeroline=False
        ),
        yaxis=dict(
            showline=True,
            linecolor='lightgrey',
            gridcolor='lightgrey',
            zeroline=False
        ),
        hovermode="x unified"
    )
    return go.figue()
