from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import uuid
import os

from services import ai_service, bigquery_service, gcs_service

app = FastAPI()

# Configurações do ambiente
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_PATH = os.getenv("BUCKET_PATH")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/verificar-sap")
async def verificar_sap(request: Request):
    payload = await request.json()
    modelo = payload.get("modelo")
    uf = payload.get("uf")
    estacao = payload.get("estacao")
    
    # Chama o serviço que você já tem no bigquery_service.py
    resultados = bigquery_service.buscar_equipamentos_por_modelo_e_local(modelo, uf, estacao)
    
    return {
        "encontrados": len(resultados) > 0,
        "data": resultados
    }
    
@app.post("/upload")
async def upload_foto(file: UploadFile = File(...)):
    try:
        id_registro = str(uuid.uuid4())
        file_name = f"{BUCKET_PATH}/{id_registro}.jpg"
        
        # 1. Upload para o GCS
        # Certifique-se que gcs_service.upload_file aceite o objeto file.file
        gcs_url = gcs_service.upload_file(file.file, file_name)
        
        # 2. Processa IA
        # Resetamos o ponteiro do arquivo antes de ler para a IA
        await file.seek(0)
        contents = await file.read()
        dados_ia = ai_service.extrair_dados_equipamento(contents)
        
        # --- NOVO LOG ---
        print(f"DEBUG: Resposta bruta da IA: {dados_ia}")
        
        return {
            "id_registro": id_registro, 
            "gcs_url": gcs_url, 
            "dados": dados_ia
        }
    except Exception as e:
        print(f"ERRO NO UPLOAD: {e}")
        return {"error": str(e)}, 500

@app.post("/salvar")
async def salvar_dados(request: Request):
    try:
        payload = await request.json()
        bigquery_service.salvar_inventario(payload)
        return {"status": "success"}
    except Exception as e:
        print(f"ERRO AO SALVAR: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8081)