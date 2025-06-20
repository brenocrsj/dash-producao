from dash import html
import dash_bootstrap_components as dbc

# <<< CORREÇÃO AQUI: Ajustando o caminho do import para incluir a pasta 'tabs' >>>
from .client_registration_tab import create_client_registration_layout
from .pricing_registration_tab import create_pricing_registration_layout
from .shift_registration_tab import create_shift_registration_layout

def create_main_cadastro_layout(df, theme):
    """
    Cria o layout principal da área de 'Cadastro' com sub-abas.
    """
    # Verifica se o DataFrame não está vazio antes de passar para os layouts filhos
    if df.empty:
        df_to_pass = None # Ou um DataFrame vazio, dependendo da lógica do filho
    else:
        df_to_pass = df

    return html.Div([
        dbc.Tabs(
            [
                dbc.Tab(
                    create_client_registration_layout(df_to_pass, theme) if df_to_pass is not None else "Carregando...",
                    label="Cadastro de Clientes", 
                    tab_id="tab-client-reg"
                ),
                dbc.Tab(
                    create_pricing_registration_layout(df_to_pass, theme) if df_to_pass is not None else "Carregando...",
                    label="Precificação", 
                    tab_id="tab-pricing-reg"
                ),
                dbc.Tab(
                    create_shift_registration_layout(), # Este não depende do df principal
                    label="Cadastro de Turno", 
                    tab_id="tab-shift-reg"
                ),
            ],
            id="cadastro-tabs",
            active_tab="tab-client-reg", # Aba que começa ativa
        )
    ])