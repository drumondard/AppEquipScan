# Usa uma imagem base leve
FROM python:3.11-slim

# Define o proxy para build e runtime
ENV http_proxy=http://10.130.12.13:82/
ENV https_proxy=http://10.130.12.13:82/
ENV HTTP_PROXY=http://10.130.12.13:82/
ENV HTTPS_PROXY=http://10.130.12.13:82/

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala o requirements.txt
COPY requirements.txt .

# Instala as dependências garantindo que o pip use o proxy e os hosts confiáveis
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    --proxy http://10.130.12.13:82/ \
    -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta
EXPOSE 8081

# Comando de execução conforme sua estrutura atual
CMD ["python", "app.py"]