# Usa uma imagem base leve
FROM python:3.11-slim

# Define o proxy para o build e para o runtime (caso necessário)
ENV http_proxy=http://10.130.12.13:82/
ENV https_proxy=http://10.130.12.13:82/
ENV HTTP_PROXY=http://10.130.12.13:82/
ENV HTTPS_PROXY=http://10.130.12.13:82/

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências de sistema básicas para evitar erros de compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala o requirements.txt
# Adicionamos --trusted-host para contornar problemas de certificado do proxy
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --proxy http://10.130.12.13:82/ \
    -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta que o Uvicorn utiliza
EXPOSE 8081

# Comando de execução
CMD ["python", "app.py"]