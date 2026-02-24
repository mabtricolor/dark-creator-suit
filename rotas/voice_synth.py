from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from pathlib import Path
import json
import uuid
import time
import hashlib
import re

import edge_tts

router = APIRouter(tags=["Voice Synth"])

# =========================
# Config
# =========================

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

def _voices_file() -> Path:
    return _repo_root() / "data" / "edge_voices.json"

def _outputs_dir() -> Path:
    out = _repo_root() / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    return out

# Cooldown simples por IP (evita spam -> menos chance de 403)
_LAST_CALL_BY_IP: dict[str, float] = {}
COOLDOWN_SECONDS = 2.5

def _client_ip(request: Request) -> str:
    # Se o proxy setar X-Forwarded-For, usa o primeiro
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def _enforce_cooldown(request: Request):
    ip = _client_ip(request)
    now = time.time()
    last = _LAST_CALL_BY_IP.get(ip, 0.0)
    if (now - last) < COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=429,
            detail=f"Muitas requisições. Aguarde {COOLDOWN_SECONDS:.0f}s e tente novamente."
        )
    _LAST_CALL_BY_IP[ip] = now

# =========================
# Voices JSON helpers
# =========================

def _load_json_file(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao ler JSON de vozes: {e}")

def _extract_list(payload):
    if isinstance(payload, list):
        return [v for v in payload if isinstance(v, dict)]
    if isinstance(payload, dict):
        for key in ("voices", "data", "items", "result"):
            val = payload.get(key)
            if isinstance(val, list):
                return [v for v in val if isinstance(v, dict)]
    raise HTTPException(
        status_code=500,
        detail="Formato inesperado do JSON de vozes. Esperado lista ou objeto com chave voices/data/items/result."
    )

def _normalize_voice(v: dict) -> dict:
    short = v.get("ShortName") or v.get("shortName") or v.get("name") or v.get("Name")
    locale = v.get("Locale") or v.get("locale")
    gender = v.get("Gender") or v.get("gender")
    friendly = v.get("FriendlyName") or v.get("friendlyName") or v.get("DisplayName") or v.get("displayName")

    if short:
        v["ShortName"] = short
    if locale:
        v["Locale"] = locale
    if gender:
        v["Gender"] = gender
    if friendly:
        v["FriendlyName"] = friendly
    if "FriendlyName" not in v and "ShortName" in v:
        v["FriendlyName"] = v["ShortName"]

    return v

def _get_voices():
    voices_path = _voices_file()
    if not voices_path.exists():
        raise HTTPException(status_code=500, detail="Arquivo data/edge_voices.json não encontrado.")

    payload = _load_json_file(voices_path)
    voices = _extract_list(payload)
    voices = [_normalize_voice(v) for v in voices]

    # Ordena (pt primeiro)
    def sort_key(x):
        loc = (x.get("Locale") or "").lower()
        return (0 if loc.startswith("pt-") else 1, (x.get("ShortName") or "").lower())

    voices.sort(key=sort_key)
    return voices

# =========================
# Routes: list voices (aliases)
# =========================

@router.get("/vozes")
@router.get("/api/tts/vozes")
@router.get("/voices")
@router.get("/api/voices")
@router.get("/api/tts/voices")
def listar_vozes():
    return _get_voices()


@router.get("/api/tts/vozes/ping")
def ping_vozes():
    vf = _voices_file()
    return {
        "ok": True,
        "voices_file_exists": vf.exists(),
        "voices_file_path": str(vf),
        "count": len(_get_voices()) if vf.exists() else 0,
    }

# =========================
# TTS Preview + Full generation
# =========================

class PreviewRequest(BaseModel):
    voz: str
    # texto vem do HTML (como você falou). Se vier vazio, usamos um texto padrão.
    texto: str | None = None
    velocidade: str = "+0%"
    pitch: str = "+0Hz"


class NarracaoRequest(BaseModel):
    texto: str
    voz: str
    velocidade: str = "+0%"
    pitch: str = "+0Hz"


def _sanitize_rate(rate: str) -> str:
    if not isinstance(rate, str):
        return "+0%"
    rate = rate.strip()
    return rate if re.match(r"^[+-]\d{1,3}%$", rate) else "+0%"


def _sanitize_pitch(pitch: str) -> str:
    if not isinstance(pitch, str):
        return "+0Hz"
    pitch = pitch.strip()
    return pitch if re.match(r"^[+-]\d{1,3}Hz$", pitch) else "+0Hz"


def _preview_cache_key(voice: str, text: str, rate: str, pitch: str) -> str:
    raw = f"{voice}||{rate}||{pitch}||{text}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:24]


async def _edge_tts_to_file(text: str, voice: str, rate: str, pitch: str, out_path: Path):
    """
    Usa edge-tts para salvar MP3.
    """
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        pitch=pitch,
    )
    await communicate.save(str(out_path))


@router.post("/api/tts/preview")
async def tts_preview(req: PreviewRequest, request: Request):
    """
    Gera um MP3 curtinho de preview.
    Retorna audio_url: /outputs/preview_xxx.mp3
    """
    _enforce_cooldown(request)

    voice = (req.voz or "").strip()
    if not voice:
        raise HTTPException(status_code=400, detail="Campo 'voz' é obrigatório.")

    text = (req.texto or "").strip()
    if not text:
        text = "Olá! Esta é uma prévia rápida da voz selecionada."

    # Limita tamanho do preview para reduzir chance de bloqueio
    text = text[:220]

    rate = _sanitize_rate(req.velocidade)
    pitch = _sanitize_pitch(req.pitch)

    out_dir = _outputs_dir()
    cache_key = _preview_cache_key(voice, text, rate, pitch)
    filename = f"preview_{cache_key}.mp3"
    out_path = out_dir / filename

    # Cache: se já existe, reaproveita
    if out_path.exists() and out_path.stat().st_size > 1000:
        return {"ok": True, "audio_url": f"/outputs/{filename}", "cached": True}

    try:
        await _edge_tts_to_file(text, voice, rate, pitch, out_path)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao gerar preview (edge-tts): {e}")

    if not out_path.exists() or out_path.stat().st_size < 1000:
        raise HTTPException(status_code=502, detail="Preview gerado, mas arquivo inválido (tamanho muito pequeno).")

    return {"ok": True, "audio_url": f"/outputs/{filename}", "cached": False}


@router.post("/gerar_narracao")
async def gerar_narracao(req: NarracaoRequest, request: Request):
    """
    Gera a narração completa.
    Retorna audio_url: /outputs/tts_xxx.mp3
    """
    _enforce_cooldown(request)

    text = (req.texto or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio.")

    voice = (req.voz or "").strip()
    if not voice:
        raise HTTPException(status_code=400, detail="Campo 'voz' é obrigatório.")

    rate = _sanitize_rate(req.velocidade)
    pitch = _sanitize_pitch(req.pitch)

    out_dir = _outputs_dir()
    filename = f"tts_{uuid.uuid4().hex}.mp3"
    out_path = out_dir / filename

    try:
        await _edge_tts_to_file(text, voice, rate, pitch, out_path)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha ao gerar narração (edge-tts): {e}")

    if not out_path.exists() or out_path.stat().st_size < 1000:
        raise HTTPException(status_code=502, detail="Narração gerada, mas arquivo inválido (tamanho muito pequeno).")

    return {"ok": True, "audio_url": f"/outputs/{filename}"}
