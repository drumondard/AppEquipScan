import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configurações de Nuvem
    GOOGLE_APPLICATION_CREDENTIALS: str = "/app/secrets/vtal-inventariorede-prd.json"
    BUCKET_NAME: str = "vtal-bucket-inventariorede-prd"
    BUCKET_PATH: str = "fotos_bot_telegram"
    
    # Configurações de IA
    LITELLM_API_KEY: str
    LITELLM_BASE_URL: str = "http://10.121.243.101:8083/v1"
    MODELO_IA: str = "gemini-3.5-flash"

    class Config:
        env_file = "/app/secrets/.env" # Caminho dentro do container

# Instancia as configurações
settings = Settings()