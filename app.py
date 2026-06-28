import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Importações dos seus serviços
from services.ai_service import extrair_dados_equipamento
from services.gcs_service import GCSService
from services.bigquery_service import salvar_inventario

# --- Configuração ---
dotenv_path = "/credenciais/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Inicializa o serviço do GCS (ajuste conforme necessário para carregar credenciais)
gcs = GCSService(credentials=None) 

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"message": "Sucesso"}
    )

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # 1. Lê os bytes da imagem
        image_bytes = await file.read()
        
        # 2. Extrai dados com a IA
        dados_ia = extrair_dados_equipamento(image_bytes)
        
        # 3. Faz upload para o GCS
        bucket = "seu-nome-de-bucket" # Ajuste aqui
        gcs_url = gcs.upload_file(bucket, image_bytes, file.filename)
        
        # 4. Salva no BigQuery
        dados_salvar = {
            "user_id": 1, # Exemplo fixo
            "idsap": "N/A",
            "hostname": "N/A",
            "dados_ia": dados_ia,
            "gcs_url": gcs_url
        }
        # Nota: Você precisará passar o bq_client corretamente
        # salvar_inventario(dados_salvar, bq_client) 
        
        return JSONResponse(content={"status": "sucesso", "dados": dados_ia})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)