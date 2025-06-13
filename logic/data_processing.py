# logic/data_processing.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache

# --- Funções de Limpeza de Dados ---

def clean_numeric_column(series: pd.Series) -> pd.Series:
    """
    Converte uma coluna para numérico, tratando vírgulas como decimais e erros.
    Valores não numéricos são preenchidos com 0.
    """
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)


def clean_text_column(series: pd.Series) -> pd.Series:
    """
    Limpa e padroniza uma coluna de texto.
    Remove espaços extras, converte para maiúsculas.
    """
    return series.astype(str).str.strip().str.upper()


# --- Carregamento e Pré-processamento de Dados ---

@lru_cache(maxsize=None)
def load_and_prepare_data() -> pd.DataFrame:
    """
    Carrega, pré-processa e une os dados das abas do Google Sheets.
    O resultado é cacheado em memória para alta performance, evitando
    novos downloads a cada atualização da página.
    """
    try:
        print("Carregando e preparando dados da frota...") # Considerar usar um logger para produção

        # URLs para exportação direta das planilhas como CSV.
        # Estas URLs são estáticas para os dados fornecidos.
        url_volume = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=0'
        url_frota = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=1061355856'
        url_precificacao = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=998298177'

        # Carregar DataFrames
        df_volume = pd.read_csv(url_volume)
        df_frota = pd.read_csv(url_frota)
        df_precificacao = pd.read_csv(url_precificacao)

        print("Dados carregados do Google Sheets com sucesso!")

        # Padronização e Limpeza de nomes de colunas
        df_volume.rename(columns={'Coluna1': 'TAG'}, inplace=True, errors='ignore')
        df_frota.rename(columns={'PLACA': 'Placa'}, inplace=True, errors='ignore')
        df_precificacao.rename(columns={'Frente': 'Destino'}, inplace=True, errors='ignore')

        # Limpeza das colunas de texto usando a função auxiliar
        for col in ['Destino', 'Material', 'Placa', 'TAG']:
            if col in df_volume.columns:
                df_volume[col] = clean_text_column(df_volume[col])

        if 'Placa' in df_frota.columns:
            df_frota['Placa'] = clean_text_column(df_frota['Placa'])

        if 'Destino' in df_precificacao.columns:
            df_precificacao['Destino'] = clean_text_column(df_precificacao['Destino'])


        # Processamento de datas e limpeza de colunas numéricas do df_volume
        df_volume['Data_Hora'] = pd.to_datetime(
            df_volume['Data'].astype(str) + ' ' + df_volume['Hora'].astype(str),
            format='mixed', errors='coerce'
        )
        df_volume.dropna(subset=['Data_Hora'], inplace=True)
        df_volume['Data_Apenas'] = df_volume['Data_Hora'].dt.date
        df_volume['Hora_Do_Dia'] = df_volume['Data_Hora'].dt.hour
        df_volume['Volume'] = clean_numeric_column(df_volume['Volume'])

        # Junção (Merge) dos dataframes para criar o dataframe final
        df_merged = pd.merge(df_volume, df_frota, on='Placa', how='left')
        df_final = pd.merge(df_merged, df_precificacao, on='Destino', how='left')

        # Limpeza final de colunas numéricas e de texto no df_final
        for col in ['Valor Bruto', 'Volume Máx']:
            if col in df_final.columns:
                df_final[col] = clean_numeric_column(df_final[col])

        for col in ['Empresa', 'Proprietario', 'Modelo', 'Tipo', 'STATUS', 'IDENTIFICAÇÃO', 'FROTA', 'CLIENTE']:
            if col in df_final.columns:
                df_final[col] = clean_text_column(df_final[col])


        # Criação de novas colunas derivadas
        if 'Volume' in df_final.columns and 'Valor Bruto' in df_final.columns:
            df_final['Valor Bruto Total'] = df_final['Volume'] * df_final['Valor Bruto']
        else:
            if 'Valor Bruto Total' not in df_final.columns:
                df_final['Valor Bruto Total'] = 0

        df_final['Turno'] = np.where(
            (df_final['Hora_Do_Dia'] >= 6) & (df_final['Hora_Do_Dia'] < 18),
            '1º Turno', '2º Turno'
        )
        df_final['Dia_Da_Semana_Num'] = pd.to_datetime(df_final['Data_Apenas']).dt.dayofweek
        
        return df_final

    except Exception as e:
        print(f"Ocorreu um erro CRÍTICO ao carregar os dados da frota: {e}")
        # Retorna um DataFrame vazio em caso de erro para evitar quebrar a aplicação
        return pd.DataFrame()


# --- Funções de Análise e Geração de Gráficos ---

def create_matrix_data(dff: pd.DataFrame) -> pd.DataFrame:
    """Cria o DataFrame formatado para a tabela da Análise Matricial."""
    if dff.empty:
        return pd.DataFrame()

    # Sua lógica completa para criar a matriz de dados...
    # (Esta é a sua lógica original, que deve ser inserida aqui)
    # Exemplo: Agrupamento básico por Data e TAG.
    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(
        Volume_Total=('Volume', 'sum'),
        N_Viagens=('Placa', 'count')  # <--- Este é o nome da coluna que está sendo criada
    ).reset_index()
    return grouped


def create_figure_from_df(fig_df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, color_sequence=None) -> go.Figure:
    """
    Cria uma figura Plotly genérica a partir de um DataFrame,
    aplicando o estilo visual do tema.
    """
    # Cores da paleta definida no assets/style.css (dark theme)
    # Convertendo HSL para string de cor para Plotly
    BG_COLOR = 'hsl(240, 10%, 10%)'  # --card (fundo dos cards e gráficos)
    TEXT_COLOR = 'hsl(240, 10%, 95%)' # --foreground (cor do texto principal)
    PRIMARY_COLOR = 'hsl(220, 90%, 55%)' # --primary (azul vibrante)
    ACCENT_COLOR = 'hsl(45, 100%, 55%)' # --accent (amarelo vibrante)
    SECONDARY_COLOR = 'hsl(240, 10%, 15%)' # --secondary (cinza médio)
    BORDER_COLOR = 'hsl(240, 10%, 20%)' # --border (cinza para bordas)

    # Sequência de cores padrão para séries de dados em gráficos
    # Começa com o azul primário e alterna com tons de cinza/secundário
    default_color_sequence = [
        PRIMARY_COLOR,
        'hsl(220, 70%, 65%)', # Azul mais claro
        SECONDARY_COLOR,
        'hsl(240, 10%, 30%)', # Cinza escuro
        ACCENT_COLOR, # Amarelo, para destaque se houver muitas séries
        'hsl(220, 50%, 75%)', # Azul mais suave
    ]

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

    # Layout padrão para os gráficos, alinhado com o tema "Azul e Amarelo"
    fig.update_layout(
        template="plotly_dark", # Mantém o template escuro
        title_x=0.5, # Centraliza o título
        paper_bgcolor='rgba(0,0,0,0)', # Fundo do papel transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo da área de plotagem transparente
        font=dict(color=TEXT_COLOR, family='Inter, sans-serif'), # Cor e fonte do texto no gráfico
        margin=dict(l=40, r=40, t=80, b=40), # Aumenta margem superior para título e subtítulos
        # Configurações para os eixos (contornos e linhas de grade)
        xaxis=dict(
            showline=True, # Mostra a linha do eixo
            linecolor=ACCENT_COLOR, # Cor da linha do eixo X (amarelo)
            linewidth=2, # Largura da linha do eixo
            gridcolor=BORDER_COLOR, # Cor das linhas de grade (cinza mais claro)
            zeroline=False # Remove a linha zero, se desejar um visual mais limpo
        ),
        yaxis=dict(
            showline=True,
            linecolor=ACCENT_COLOR,
            linewidth=2,
            gridcolor=BORDER_COLOR,
            zeroline=False
        ),
        # Adicionar hovermode para melhor interatividade
        hovermode="x unified"
    )
    return fig