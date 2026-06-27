from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from services.ai_service import extrair_dados_equipamento
from services.gcs_service import GCSService
from services.bigquery_service import salvar_inventario
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import uuid
from dotenv import load_dotenv

# Carrega o .env que montaremos via volume no Docker
load_dotenv("/app/.env") 

app = FastAPI()

# Configuração de caminhos baseados no diretório do container
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Inicialização com verificação de existência do arquivo de credenciais
cred_path = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
if not cred_path or not os.path.exists(cred_path):
    raise FileNotFoundError(f"Arquivo de credenciais não encontrado em: {cred_path}")

credentials = service_account.Credentials.from_service_account_file(cred_path)
gcs_service = GCSService(credentials)
bq_client = bigquery.Client(credentials=credentials, project="vtal-inventariorede-prd")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_foto(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    # Processamento
    dados = extrair_dados_equipamento(image_bytes)
    
    blob_name = f"web_upload/{uuid.uuid4()}.jpg"
    gcs_url = gcs_service.upload_file("vtal-bucket-inventariorede-prd", image_bytes, blob_name)
    
    salvar_inventario({
        'idsap': 'WEB_UPLOAD',
        'hostname': 'N/A',
        'loc': '0,0',
        'dados_ia': dados,
        'user_id': 0,
        'gcs_url': gcs_url
    }, bq_client)
    
    return {"status": "sucesso", "dados": dados, "url": gcs_url}