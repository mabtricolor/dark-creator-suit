from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter(tags=["Voice Synth"])

@router.get("/vozes")
@router.get("/api/tts/vozes")
@router.get("/voices")
@router.get("/api/voices")
@router.get("/api/tts/voices")
def listar_vozes():
    base_dir = Path(__file__).resolve().parent.parent
    voices_path = base_dir / "data" / "edge_voices.json"

    if not voices_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Arquivo data/edge_voices.json não encontrado. Adicione o JSON das vozes no repo."
        )

    try:
        return json.loads(voices_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao ler JSON de vozes: {e}")
