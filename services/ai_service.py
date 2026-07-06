import base64
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Carrega .env
dotenv_path = "/AppEquipScan/secrets/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)

client = OpenAI(
    api_key=os.getenv("LITELLM_API_KEY"),
    base_url=os.getenv("LITELLM_BASE_URL", "http://10.121.243.101:8083/v1")
)

def extrair_dados_equipamento(image_bytes: bytes) -> str:
    try:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
        prompt = (
            "Analise esta imagem de uma etiqueta de equipamento de rede. "
            "Extraia os dados e responda APENAS com um JSON puro, sem markdown, sem explicações. "
            "Use estas chaves exatas: 'fabricante', 'modelo', 'funcao', 'numero_serie', 'hostname'. "
            "Se algum dado não for encontrado, coloque null."
        )

        # Usando o modelo definido no seu ambiente ou o que o seu servidor LiteLLM suporta
        # Tente "gemini-3.5-flash" ou apenas "gemini" se o 3.5 falhar
        response = client.chat.completions.create(
            model=os.getenv("MODELO_IA", "gemini-3.5-flash"), 
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]}
            ],
            temperature=0.0
        )

        raw_content = response.choices[0].message.content.strip()
        # Remove possíveis blocos de código markdown que a IA insiste em colocar
        clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_content, flags=re.MULTILINE)
        return clean_json.strip()

    except Exception as e:
        print(f"DEBUG ERRO IA: {str(e)}") # Isso aparecerá nos logs do docker
        return json.dumps({
            "fabricante": None, "modelo": None, "funcao": None, 
            "numero_serie": None, "hostname": None, 
            "error": "Falha na IA"
        })