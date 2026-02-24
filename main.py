from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from rotas.ai_script_forge import router as script_forge_router
from rotas.voice_synth import router as voice_router  # <-- agora TUDO está aqui (vozes + preview + gerar_narracao)

app = FastAPI(
    title="Dark Creator Suit",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Routers
app.include_router(script_forge_router)
app.include_router(voice_router)

# Paths
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
OUTPUTS_DIR = BASE_DIR / "outputs"

# Static mounts
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

@app.get("/")
def home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/health")
def health():
    return {"ok": True}
    
