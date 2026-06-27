import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# --- Configuração de Ambiente ---
# Carrega as variáveis de ambiente do arquivo .env montado no container
dotenv_path = "/app/credenciais/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"DEBUG: Arquivo .env carregado de {dotenv_path}")
else:
    print(f"AVISO: Arquivo .env não encontrado em {dotenv_path}")

# Recupera o caminho da chave JSON injetado via variável de ambiente
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_SERV_INVENTARIO")
print(f"DEBUG: Caminho lido do .env: {GCP_CREDENTIALS_PATH}")

# --- Configuração da App ---
app = FastAPI()

# Define o diretório onde os templates HTML estão localizados
# Certifique-se de que a pasta 'templates' existe no mesmo nível deste arquivo
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Endpoint principal.
    A sintaxe correta do TemplateResponse exige que 'request' seja um argumento nomeado.
    """
    try:
        # Sintaxe corrigida para evitar TypeError: unhashable type: 'dict'

    return templates.TemplateResponse(request=request, name="index.html", context={})
    except Exception as e:
        # Retorna o erro no navegador caso o template não seja encontrado ou haja falha de renderização
        return HTMLResponse(content=f"<h1>Erro Interno: {str(e)}</h1>", status_code=500)

@app.get("/health")
async def health():
    """Endpoint para verificar se a aplicação está viva e o path da chave está correto."""
    return {
        "status": "ok", 
        "config_path": GCP_CREDENTIALS_PATH,
        "path_exists": os.path.exists(GCP_CREDENTIALS_PATH) if GCP_CREDENTIALS_PATH else False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)