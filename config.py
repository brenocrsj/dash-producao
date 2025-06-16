# config.py
THEME_COLORS = {
    'dark': {
        'foreground': 'hsl(220, 15%, 90%)',
        'text': 'hsl(220, 15%, 90%)', # Adicionado para uso em gráficos e texto geral
        'primary': 'hsl(210, 85%, 65%)',
        'secondary': 'hsl(38, 92%, 60%)', # Adicionado, pois 'chart_2' é usado no gráfico semanal
        'accent': 'hsl(38, 92%, 60%)',
        'chart_1': 'hsl(210, 85%, 65%)',
        'chart_2': 'hsl(38, 92%, 60%)',
        'chart_3': 'hsl(140, 70%, 55%)',
        'chart_4': 'hsl(260, 70%, 75%)',
        'chart_5': 'hsl(190, 70%, 60%)',
        'card_bg': 'hsl(220, 15%, 20%)', # Cor de fundo para os cards e gráficos
        'grid_line': 'hsl(220, 10%, 30%)', # Cor das linhas de grade nos gráficos
    }
}

SECRET_KEY = 'S969f11127790ba12575f75b8ef9a91fc7e5d61fab65bbcaa'