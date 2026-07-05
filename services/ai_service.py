import base64
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# 1. Carrega explicitamente o .env do local especificado
dotenv_path = "/AppEquipScan/secrets/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    print(f"DEBUG: Variáveis carregadas de {dotenv_path}")

# 2. Inicialização do Cliente
# O os.getenv agora buscará o valor carregado pelo load_dotenv acima
client = OpenAI(
    api_key=os.getenv("LITELLM_API_KEY"),
    base_url=os.getenv("LITELLM_BASE_URL", "http://10.121.243.101:8083/v1")
)

def extrair_dados_equipamento(image_bytes: bytes) -> str:
    """
    Processa os bytes da imagem, extrai JSON via Regex e retorna string JSON.
    """
    try:
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        # Refinamento do prompt para garantir que o formato seja IMPECÁVEL para o Gemini
        prompt = (
            "Analise a imagem da etiqueta. Retorne APENAS um JSON válido. "
            "Não inclua markdown, não inclua blocos de código. "
            "Use exatamente estas chaves: 'fabricante', 'modelo', 'funcao', 'numero_serie'."
        )

        response = client.chat.completions.create(
            model="gemini-3.5-flash",
            #model='gemini-2.5-flash', ### Descontinuado
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
                        }
                    ]
                }
            ],
            temperature=0.1
        )

        raw_content = response.choices[0].message.content.strip()
        
        # Regex para isolar o JSON ignorando markdown ou textos extras
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if not match:
            # Caso a IA falhe em responder o formato esperado, logamos o conteúdo para debug
            print(f"DEBUG: Resposta IA inesperada: {raw_content}")
            raise ValueError("IA não retornou um JSON válido")
            
        json_str = match.group(0).replace("```json", "").replace("```", "").strip()
        
        # Validação final
        json.loads(json_str)
        
        print(f"DEBUG: IA extraiu com sucesso.")
        return json_str

    except Exception as e:
        erro_msg = f"Erro no AI_SERVICE: {str(e)}"
        print(f"DEBUG: {erro_msg}")
        return json.dumps({"error": "Falha na IA", "detalhes": str(e)[:50]})