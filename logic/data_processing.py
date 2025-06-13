# logic/data_processing.py

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache

def clean_numeric_column(series: pd.Series) -> pd.Series:
    """Converte uma coluna para numérico, tratando vírgulas e erros."""
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

def clean_text_column(series: pd.Series) -> pd.Series:
    """Limpa e padroniza uma coluna de texto (remove espaços e capitaliza)."""
    return series.astype(str).str.strip().str.upper()

@lru_cache(maxsize=None)
def load_and_prepare_data() -> pd.DataFrame:
    """
    Carrega, pré-processa e une os dados das abas do Google Sheets.
    O resultado é cacheado em memória para alta performance, evitando
    novos downloads a cada atualização da página.
    """
    try:
        print("Carregando e preparando dados da frota...")
        # URLs para exportação direta das planilhas como CSV.
        url_volume = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=0'
        url_frota = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=1061355856'
        url_precificacao = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv&gid=998298177'

        df_volume = pd.read_csv(url_volume)
        df_frota = pd.read_csv(url_frota)
        df_precificacao = pd.read_csv(url_precificacao)

        print("Dados carregados do Google Sheets com sucesso!")

        # Padronização de nomes de colunas
        df_volume.rename(columns={'Coluna1': 'TAG'}, inplace=True, errors='ignore')
        df_frota.rename(columns={'PLACA': 'Placa'}, inplace=True, errors='ignore')
        df_precificacao.rename(columns={'Frente': 'Destino'}, inplace=True, errors='ignore')

        # Limpeza das colunas de texto
        for col in ['Destino', 'Material', 'Placa', 'TAG']:
            if col in df_volume.columns: df_volume[col] = clean_text_column(df_volume[col])
        if 'Placa' in df_frota.columns: df_frota['Placa'] = clean_text_column(df_frota['Placa'])
        if 'Destino' in df_precificacao.columns: df_precificacao['Destino'] = clean_text_column(df_precificacao['Destino'])

        # Processamento de datas e limpeza de colunas numéricas
        df_volume['Data_Hora'] = pd.to_datetime(
            df_volume['Data'].astype(str) + ' ' + df_volume['Hora'].astype(str),
            format='mixed', errors='coerce'
        )
        df_volume.dropna(subset=['Data_Hora'], inplace=True)
        df_volume['Data_Apenas'] = df_volume['Data_Hora'].dt.date
        df_volume['Hora_Do_Dia'] = df_volume['Data_Hora'].dt.hour
        df_volume['Volume'] = clean_numeric_column(df_volume['Volume'])

        # Junção (Merge) dos dataframes
        df_merged = pd.merge(df_volume, df_frota, on='Placa', how='left')
        df_final = pd.merge(df_merged, df_precificacao, on='Destino', how='left')

        # Limpeza final e criação de novas colunas
        for col in ['Valor Bruto', 'Volume Máx']:
            if col in df_final.columns: df_final[col] = clean_numeric_column(df_final[col])
        for col in ['Empresa', 'Proprietario', 'Modelo', 'Tipo', 'STATUS', 'IDENTIFICAÇÃO', 'FROTA', 'CLIENTE']:
            if col in df_final.columns: df_final[col] = clean_text_column(df_final[col])

        if 'Volume' in df_final.columns and 'Valor Bruto' in df_final.columns:
            df_final['Valor Bruto Total'] = df_final['Volume'] * df_final['Valor Bruto']
        else:
            if 'Valor Bruto Total' not in df_final.columns: df_final['Valor Bruto Total'] = 0

        df_final['Turno'] = np.where((df_final['Hora_Do_Dia'] >= 6) & (df_final['Hora_Do_Dia'] < 18), '1º Turno', '2º Turno')
        df_final['Dia_Da_Semana_Num'] = pd.to_datetime(df_final['Data_Apenas']).dt.dayofweek
        
        return df_final

    except Exception as e:
        print(f"Ocorreu um erro CRÍTICO ao carregar os dados da frota: {e}")
        return pd.DataFrame()


def create_matrix_data(dff: pd.DataFrame) -> pd.DataFrame:
    """Cria o DataFrame formatado para a tabela da Análise Matricial."""
    if dff.empty: return pd.DataFrame()

    # Lógica completa para criar a matriz de dados...
    # (Esta é a sua lógica original, que deve ser inserida aqui)
    # Por exemplo:
    grouped = dff.groupby(['Data_Apenas', 'TAG']).agg(
        Volume_Total=('Volume', 'sum'),
        N_Viagens=('Placa', 'count')
    ).reset_index()
    # Este é um exemplo simplificado. Insira sua lógica completa aqui.
    return grouped

def create_figure_from_df(fig_df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str, color_sequence=None) -> go.Figure:
    """Cria uma figura Plotly genérica a partir de um DataFrame."""
    if chart_type == 'bar':
        fig = px.bar(fig_df, x=x_col, y=y_col, title=title, text_auto='.2s', color_discrete_sequence=color_sequence)
    elif chart_type == 'line':
        fig = px.line(fig_df, x=x_col, y=y_col, title=title, markers=True, color_discrete_sequence=color_sequence)
    else:
        fig = go.Figure()

    # Layout padrão para os gráficos
    fig.update_layout(
        template="plotly_dark", title_x=0.5, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig