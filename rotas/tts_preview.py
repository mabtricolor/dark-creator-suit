from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid
import edge_tts
import asyncio

router = APIRouter(prefix="/api/tts", tags=["TTS"])

class PreviewRequest(BaseModel):
    voz: str
    texto: str
    rate: str = "+0%"   # ex: "+10%"
    pitch: str = "+0Hz" # ex: "+2Hz"

def _outputs_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "outputs"

@router.post("/preview")
async def preview(req: PreviewRequest):
    text = (req.texto or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio.")

    out_dir = _outputs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    filename = f"preview_{uuid.uuid4().hex}.mp3"
    out_path = out_dir / filename

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=req.voz,
            rate=req.rate,
            pitch=req.pitch,
        )
        await communicate.save(str(out_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar preview: {e}")

    # URL pública do arquivo
    return {"ok": True, "audio_url": f"/outputs/{filename}"}
