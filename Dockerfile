# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o PostgreSQL e compiladores
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt (que está na mesma pasta web-scraping)
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte e cria as pastas de dados
COPY src/ src/
RUN mkdir -p inputs outputs

# Comando para manter o container vivo (para rodarmos comandos manualmente)
CMD ["tail", "-f", "/dev/null"]