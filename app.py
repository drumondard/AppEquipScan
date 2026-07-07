import os
import uuid
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Importação dos seus serviços
from services import ai_service, bigquery_service, gcs_service

app = FastAPI()

# Configurações de diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Configurações de ambiente - PADRONIZADO EM MAIÚSCULAS
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_PATH = os.getenv("BUCKET_PATH", "fotos_bot_telegram") 

if not BUCKET_NAME:
    raise RuntimeError("ERRO: BUCKET_NAME não foi carregado. Verifique seu arquivo .env!")

# Montagem de estáticos
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/verificar-sap")
async def verificar_sap(request: Request):
    try:
        payload = await request.json()
        modelo = payload.get("modelo")
        uf = payload.get("uf")
        estacao = payload.get("estacao")
        resultados = bigquery_service.buscar_equipamentos_por_modelo_e_local(modelo, uf, estacao)
        return {"encontrados": len(resultados) > 0, "data": resultados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/upload")
async def upload_foto(file: UploadFile = File(...)):
    # Usando a variável global BUCKET_PATH corretamente
    print(f"DEBUG: BUCKET_NAME={BUCKET_NAME}")
    print(f"DEBUG: BUCKET_PATH={BUCKET_PATH}")
    
    try:
        id_registro = str(uuid.uuid4())
        file_name = f"{BUCKET_PATH}/{id_registro}.jpg"
        print(f"DEBUG: Caminho do arquivo={file_name}")
        
        gcs_url = gcs_service.upload_file(file.file, file_name)
        
        await file.seek(0)
        contents = await file.read()
        dados_ia = ai_service.extrair_dados_equipamento(contents)
        
        return {
            "id_registro": id_registro, 
            "gcs_url": gcs_url, 
            "dados": dados_ia
        }
    except Exception as e:
        print(f"ERRO NO UPLOAD: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/salvar")
async def salvar_dados(request: Request):
    try:
        payload = await request.json()
        bigquery_service.salvar_inventario(payload)
        return {"status": "success"}
    except Exception as e:
        print(f"ERRO AO SALVAR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8081)