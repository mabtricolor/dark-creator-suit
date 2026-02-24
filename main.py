from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from rotas.ai_script_forge import router as script_forge_router
from rotas.voice_synth import router as voice_router
from fastapi.staticfiles import StaticFiles
from rotas.tts_preview import router as tts_preview_router

app = FastAPI(
    title="Dark Creator Suit",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 1) Rotas (cada ferramenta em um arquivo separado)
app.include_router(script_forge_router)
app.include_router(voice_router)
app.include_router(tts_preview_router)

# 2) Frontend estático
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

app.mount("/outputs", StaticFiles(directory=str(BASE_DIR / "outputs")), name="outputs")


@app.get("/")
def home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/health")
def health():
    return {"ok": True}
