# config.py
THEME_COLORS = {
    'dark': {
        'foreground': 'hsl(0, 0%, 0%)', # Cor primária para o texto geral do aplicativo e elementos de interface.
        'text': 'hsl(0, 0%, 0%)',       # Cor do texto dentro dos elementos gráficos (títulos, rótulos, legendas).
        'primary': 'hsl(210, 85%, 65%)',    # Cor principal de destaque para elementos interativos e barras de gráficos.
        'secondary': 'hsl(38, 92%, 60%)',   # Cor secundária de destaque, usada para diferenciar métricas em gráficos de linha.
        'accent': 'hsl(38, 92%, 60%)',      # Cor de acento para elementos específicos, pode ser similar à 'secondary'.
        'chart_1': 'hsl(210, 85%, 65%)',    # Cor específica para o primeiro conjunto de dados em gráficos.
        'chart_2': 'hsl(38, 92%, 60%)',     # Cor específica para o segundo conjunto de dados em gráficos.
        'chart_3': 'hsl(140, 70%, 55%)',    # Cor específica para o terceiro conjunto de dados em gráficos.
        'chart_4': 'hsl(260, 70%, 75%)',    # Cor específica para o quarto conjunto de dados em gráficos.
        'chart_5': 'hsl(190, 70%, 60%)',    # Cor específica para o quinto conjunto de dados em gráficos.
        'card_bg': 'hsla(220, 15%, 20%, 0)', # Cor de fundo para os cards de KPI e áreas de plotagem dos gráficos (definido como transparente).
        'grid_line': 'hsl(220, 10%, 30%)',  # Cor das linhas de grade dentro dos gráficos para melhor visualização.
    }
}

SECRET_KEY = 'S969f11127790ba12575f75b8ef9a91fc7e5d61fab65bbcaa'