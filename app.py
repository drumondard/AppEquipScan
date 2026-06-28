import os
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

ID_BUCKET_FOTOS='vtal-bucket-inventariorede-prd/fotos_bot_telegram'

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        return templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context={"message": "Sucesso"}
        )
    except Exception as e:
        return HTMLResponse(content=f"<h1>Erro ao carregar template: {str(e)}</h1>", status_code=500)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # 1. Preparação dos serviços
        # O GCS utiliza a variável GOOGLE_APPLICATION_CREDENTIALS definida no docker-compose
        gcs = GCSService(credentials=None)
        bq_client = bigquery.Client()
        
        # 2. Processamento da imagem
        image_bytes = await file.read()
        dados_ia = extrair_dados_equipamento(image_bytes)
        
        # 3. Upload para GCS
        # Substitua 'NOME_DO_SEU_BUCKET' pelo nome real do seu bucket no GCS
        gcs_url = gcs.upload_file(ID_BUCKET_FOTOS, image_bytes, file.filename)
        
        # 4. Salvar no BigQuery
        dados_para_bq = {
            "user_id": 123,  # Pode integrar com autenticação real depois
            "idsap": "N/A",
            "hostname": "N/A",
            "dados_ia": dados_ia,
            "gcs_url": gcs_url
        }
        salvar_inventario(dados_para_bq, bq_client)
        
        return JSONResponse(content={"status": "sucesso", "dados": dados_ia})
        
    except Exception as e:
        import traceback
        traceback.print_exc() # Isso imprimirá o erro detalhado nos logs do Docker
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)