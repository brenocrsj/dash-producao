# components/header.py (Versão Final Corrigida)

from dash import html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def create_header():
    """Cria o cabeçalho superior do site (SiteHeader)."""
    
    user_avatar = html.Div(
        DashIconify(icon="lucide:user-circle", width=24, height=24),
        className="avatar-button"
    )
    
    user_dropdown = dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem("Minha Conta", header=True),
            dbc.DropdownMenuItem(
                [DashIconify(icon="lucide:settings", width=16, className="me-2"), "Configurações"],
                href="/settings",
            ),
            dbc.DropdownMenuItem(
                [DashIconify(icon="lucide:log-out", width=16, className="me-2"), "Sair"],
                href="/logout",
            ),
        ],
        label=user_avatar,
        align_end=True,
        # CORREÇÃO APLICADA AQUI:
        toggle_class_name="nav-link",
        color="transparent"
    )

    header = html.Header(
        [
            html.Button(DashIconify(icon="lucide:menu"), className="sidebar-trigger d-md-none"),
            html.Div(html.H1(id="page-title"), className="flex-grow-1"),
            user_dropdown,
        ],
        className="site-header"
    )
    
    return header