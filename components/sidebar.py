# components/sidebar.py
from dash import html, dcc
import dash_bootstrap_components as dbc


def create_sidebar():
    """
    Esta função agora retorna um Div vazio (escondido), pois a barra lateral foi substituída
    por uma barra superior de navegação. Seu conteúdo foi movido para o header.py.
    """
    return html.Div(style={'display': 'none'})