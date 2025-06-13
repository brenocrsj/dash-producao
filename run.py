# run.py

# Importa as instâncias 'app' e 'server' que são definidas globalmente em app.py
from app import app, server 

if __name__ == '__main__':
    # Aqui você pode rodar o servidor Dash para desenvolvimento
    # A variável 'app' é a instância do Dash, e 'server' é a instância do Flask
    # CORRIGIDO: app.run_server() foi substituído por app.run()
    app.run(debug=True) # Use app.run() em vez de app.run_server()