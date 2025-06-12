# run.py (versão corrigida)

from app import app
# A importação do 'server' não é estritamente necessária aqui, mas não causa problemas.

# Este bloco só é executado quando você roda `python run.py`
if __name__ == '__main__':
    # CORREÇÃO: Usamos app.run() que é o comando para as versões mais novas do Dash.
    app.run(debug=True, port=8080)