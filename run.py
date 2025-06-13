# run.py
from app import create_app

app, server = create_app()

if __name__ == '__main__':
    server.run(debug=True, port=8080)