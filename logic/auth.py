# logic/auth.py
import flask # Adicionei esta importação caso não estivesse

# Simplesmente para demonstração. Em um app real, use um banco de dados, hash de senhas, etc.
VALID_USERNAME_PASSWORD = {
    'admin': 'admin123',
    'breno': 'breno123'
}

def check_credentials(username, password):
    """
    Verifica as credenciais do usuário.
    """
    if username in VALID_USERNAME_PASSWORD and VALID_USERNAME_PASSWORD[username] == password:
        print(f"DEBUG: Credenciais válidas para {username}") # DEBUG PRINT
        return True
    print(f"DEBUG: Credenciais inválidas para {username}. Senha fornecida: {password}") # DEBUG PRINT
    return False

def logout_user():
    """
    Limpa a sessão do usuário.
    """
    if 'logged_in' in flask.session:
        del flask.session['logged_in']
    if 'username' in flask.session:
        del flask.session['username']