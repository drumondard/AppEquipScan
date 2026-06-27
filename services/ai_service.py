import json
from google import genai
from google.genai import types

def extrair_dados_equipamento(image_bytes: bytes) -> dict:
    client = genai.Client()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg')
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "fabricante": {"type": "STRING"},
                "modelo": {"type": "STRING"},
                "funcao": {"type": "STRING"},
                "serial_number": {"type": "STRING"}
            }
        }
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=["Analise este equipamento e extraia os dados em JSON.", image_part],
        config=config
    )
    return json.loads(response.text)