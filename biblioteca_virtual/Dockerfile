# Usa uma imagem oficial do Python baseada no Debian Bullseye (Linux)
FROM python:3.11-slim-bullseye

# Define variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala as dependências do sistema necessárias para WeasyPrint/GTK+ e PostgreSQL
# O comando apt-get update é necessário antes de instalar
# O --no-install-recommends economiza espaço
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requirements primeiro (para aproveitar o cache do Docker)
COPY requirements.txt /app/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código do seu projeto para dentro do container
COPY . /app/

# Expõe a porta que o Gunicorn vai usar (o Render usa 10000 por padrão)
EXPOSE 10000

# Comando para rodar o Gunicorn (será especificado no Render)
# ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:10000", "biblioteca_virtual.wsgi:application"]
# (Comentamos o ENTRYPOINT porque vamos definir isso na UI do Render)