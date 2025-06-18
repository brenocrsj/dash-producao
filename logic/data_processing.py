# logic/data_processing.py

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functools import lru_cache
from datetime import datetime
import database

# --- Funções de Limpeza de Dados (sem alterações) ---
def clean_numeric_column(series: pd.Series) -> pd.Series:
    """Converte uma coluna para numérico, tratando vírgulas como decimais e erros."""
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0)

def clean_text_column(series: pd.Series) -> pd.Series:
    """Limpa e padroniza uma coluna de texto."""
    return series.astype(str).str.strip().str.upper()

@lru_cache(maxsize=None)
def load_and_prepare_data() -> pd.DataFrame:
    """
    Carrega, padroniza, pré-processa e une os dados de todas as fontes de forma segura e robusta.
    """
    try:
        print("--- INICIANDO CARREGAMENTO DE DADOS ---")

        # URLs com timestamp para evitar cache
        timestamp = datetime.now().timestamp()
        base_url = 'https://docs.google.com/spreadsheets/d/1gUfUjoYN-zKOuAmzzl4AP35wz0PeaR5eGm4B34Cj0LI/export?format=csv'
        url_volume = f'{base_url}&gid=0&timestamp={timestamp}'
        url_frota = f'{base_url}&gid=1061355856&timestamp={timestamp}'

        # 1. Carregamento dos dados
        df_volume = pd.read_csv(url_volume)
        df_frota = pd.read_csv(url_frota)
        all_pricing_from_db = database.get_all_pricing()
        df_precificacao = pd.DataFrame(all_pricing_from_db, columns=['id', 'destination', 'price_per_ton', 'start_date', 'end_date'])
        print(f"-> Dados carregados: {df_volume.shape[0]} de volume, {df_frota.shape[0]} de frota, {len(df_precificacao)} de preços.")

        # 2. Padronização de Colunas
        df_volume.columns = df_volume.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
        df_frota.columns = df_frota.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
        if not df_precificacao.empty:
            df_precificacao.columns = df_precificacao.columns.astype(str).str.strip().str.lower()
        
        # 3. Preparação e Limpeza
        df_volume.rename(columns={'unnamed:_0': 'tag'}, inplace=True, errors='ignore')
        df_volume['data_hora'] = pd.to_datetime(df_volume['data'].astype(str) + ' ' + df_volume['hora'].astype(str), format='mixed', errors='coerce')
        df_volume.dropna(subset=['data_hora'], inplace=True)
        df_volume['data_apenas'] = df_volume['data_hora'].dt.date
        df_volume['hora_do_dia'] = df_volume['data_hora'].dt.hour
        df_volume['volume'] = clean_numeric_column(df_volume['volume'])
        
        if 'placa' in df_frota.columns:
            df_frota['placa'] = clean_text_column(df_frota['placa'])
            df_frota.drop_duplicates(subset=['placa'], keep='first', inplace=True)

        if not df_precificacao.empty:
            df_precificacao.rename(columns={'price_per_ton': 'valor_bruto'}, inplace=True)
            df_precificacao['start_date'] = pd.to_datetime(df_precificacao['start_date']).dt.date
            df_precificacao['end_date'] = pd.to_datetime(df_precificacao['end_date']).dt.date
            if 'destination' in df_precificacao.columns:
                df_precificacao['destino'] = clean_text_column(df_precificacao['destination'])
            df_precificacao['valor_bruto'] = clean_numeric_column(df_precificacao['valor_bruto'])
        
        # 4. Junção (Merge)
        df_final = pd.merge(df_volume, df_frota, on='placa', how='left')
        
        if not df_precificacao.empty:
            df_final = pd.merge(df_final, df_precificacao, on='destino', how='left')
            condition = (
                (df_final['data_apenas'] >= df_final['start_date']) &
                (df_final['data_apenas'] <= df_final['end_date'])
            )
            df_final['valor_bruto_total'] = np.where(condition, df_final['volume'] * df_final['valor_bruto'], 0)
            df_final['valor_bruto'] = np.where(condition, df_final['valor_bruto'], 0)
        else:
            df_final['valor_bruto'] = 0
            df_final['valor_bruto_total'] = 0

        # <<< CORREÇÃO AQUI: REINTRODUZINDO O CÁLCULO DO TURNO >>>
        if 'hora_do_dia' in df_final.columns:
            df_final['turno'] = np.where(
                (df_final['hora_do_dia'] >= 6) & (df_final['hora_do_dia'] < 18), 
                '1º Turno', 
                '2º Turno'
            )
        else:
            df_final['turno'] = 'N/A'

        if 'data_apenas' in df_final.columns:
            df_final['dia_da_semana_num'] = pd.to_datetime(df_final['data_apenas']).dt.dayofweek
        else:
            df_final['dia_da_semana_num'] = None

        # 6. Renomeação Final
        df_final.rename(columns={
            'data_hora': 'Data_Hora', 'data_apenas': 'Data_Apenas', 'hora_do_dia': 'Hora_Do_Dia',
            'volume': 'Volume', 'placa': 'Placa', 'destino': 'Destino', 'material': 'Material',
            'valor_bruto': 'Valor Bruto', 'valor_bruto_total': 'Valor Bruto Total', 'tag': 'TAG',
            'empresa': 'Empresa', 'turno': 'Turno', 'dia_da_semana_num': 'Dia_Da_Semana_Num'
        }, inplace=True, errors='ignore')

        print("Processamento de dados concluído.")
        return df_final
    except Exception as e:
        print(f"ERRO CRÍTICO em load_and_prepare_data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"!!!!!!!! OCORREU UM ERRO CRÍTICO AO CARREGAR OS DADOS !!!!!!!!")
        print(f"Detalhe do erro: {e}")
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
    return pd.DataFrame()


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