import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from services.ai_service import extrair_dados_equipamento
from services.gcs_service import GCSService

# --- Configuração ---
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
        # Inicializa o serviço aqui dentro para evitar erro no boot do app
        gcs = GCSService(credentials=None) # Usará o ambiente definido no Docker
        
        image_bytes = await file.read()
        
        # Extrai dados com a IA
        dados_ia = extrair_dados_equipamento(image_bytes)
        
        # Upload para o GCS
        # Substitua 'seu-nome-de-bucket' pelo nome real do seu bucket
        gcs_url = gcs.upload_file("seu-nome-de-bucket", image_bytes, file.filename)
        
        return JSONResponse(content={"status": "sucesso", "dados": dados_ia, "url": gcs_url})
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)