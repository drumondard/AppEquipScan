import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# --- Configuração de Ambiente ---
dotenv_path = "/credenciais/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        # AQUI PRECISA DE ESPAÇOS (ex: 4 espaços) ANTES DO 'return'
        return templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context={"message": "Sucesso"}
        )
    except Exception as e:
        # AQUI TAMBÉM PRECISA DE ESPAÇOS (ex: 4 espaços) ANTES DO 'return'
        return HTMLResponse(content=f"<h1>Erro: {str(e)}</h1>", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)