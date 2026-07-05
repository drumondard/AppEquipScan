import uuid
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import bigquery
from services.ai_service import extrair_dados_equipamento
from services.gcs_service import GCSService
from services.bigquery_service import salvar_inventario

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        gcs = GCSService()
        image_bytes = await file.read()
        
        # Extração via IA
        dados_ia = extrair_dados_equipamento(image_bytes)
        
        # Upload para GCS
        gcs_url = gcs.upload_file('vtal-bucket-inventariorede-prd', image_bytes, f"fotos/{file.filename}")
        id_reg = str(uuid.uuid4())
        
        return JSONResponse(content={
            "status": "sucesso", 
            "dados": dados_ia, 
            "id_registro": id_reg, 
            "gcs_url": gcs_url
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/salvar")
async def salvar(request: Request):
    try:
        dados = await request.json()
        bq_client = bigquery.Client(project="vtal-inventariorede-prd")
        salvar_inventario(dados, bq_client)
        return JSONResponse(content={"status": "sucesso"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)