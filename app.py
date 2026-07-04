import os
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Importação dos serviços
from services.ai_service import extrair_dados_equipamento
from services.gcs_service import GCSService
from services.bigquery_service import salvar_inventario
from google.cloud import bigquery

# --- Configuração ---
load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")

ID_BUCKET_FOTOS = 'vtal-bucket-inventariorede-prd'

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"message": "Sucesso"})

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Instancie o serviço sem argumentos
        gcs = GCSService()
        bq_client = bigquery.Client(project="vtal-inventariorede-prd")
        
        image_bytes = await file.read()
        dados_ia = extrair_dados_equipamento(image_bytes)
        
        # Upload para GCS
        caminho_blob = f"fotos_bot_telegram/{file.filename}"
        gcs_url = gcs.upload_file(ID_BUCKET_FOTOS, image_bytes, caminho_blob)
        
        # Salvar no BigQuery
        dados_para_bq = {
            "user_id": 123,
            "idsap": "N/A",
            "hostname": "N/A",
            "dados_ia": dados_ia,
            "gcs_url": gcs_url
        }
        salvar_inventario(dados_para_bq, bq_client)
        
        return JSONResponse(content={"status": "sucesso", "dados": dados_ia})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)