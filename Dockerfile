# Usa uma imagem oficial do Python como base
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /code

# Copia o arquivo de requisitos para o contêiner
COPY requirements.txt .

# Instala as bibliotecas listadas no requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copia todo o resto do seu projeto (app.py, etc.) para o contêiner
COPY . .

# Expõe a porta que o Gunicorn vai usar (padrão do Hugging Face)
EXPOSE 7860

# Comando para iniciar o aplicativo usando Gunicorn
# O --bind 0.0.0.0:7860 diz ao Gunicorn para escutar na porta correta
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:7860", "app:server"]