from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(tags=["Voice Synth"])

@router.get("/vozes")
@router.get("/api/tts/vozes")
def listar_vozes():
    base_dir = Path(__file__).resolve().parent.parent
    voices_path = base_dir / "data" / "edge_voices.json"

    if not voices_path.exists():
        raise HTTPException(status_code=500, detail="Arquivo data/edge_voices.json não encontrado.")

    try:
        payload = json.loads(voices_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao ler JSON de vozes: {e}")

    # NORMALIZA para sempre retornar LISTA
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        # tenta chaves comuns
        for key in ("voices", "data", "items", "result"):
            val = payload.get(key)
            if isinstance(val, list):
                return val

    raise HTTPException(
        status_code=500,
        detail="Formato inesperado do JSON de vozes. Esperado lista ou objeto com chave 'voices'/'data'."
    )
