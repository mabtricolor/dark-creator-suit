from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
from typing import Any, Dict, List

router = APIRouter(tags=["Voice Synth"])


# --------- Helpers ---------

def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao ler JSON de vozes: {e}")


def _extract_list(payload: Any) -> List[Dict[str, Any]]:
    """
    Aceita:
      - lista direta [ {...}, {...} ]
      - dict com chaves comuns {"voices":[...]} / {"data":[...]} / {"items":[...]} / {"result":[...]}
    Retorna sempre lista de dicts.
    """
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


def _normalize_voice(v: Dict[str, Any]) -> Dict[str, Any]:
    """
    Padroniza os campos mais comuns para o formato que o frontend costuma esperar.
    - ShortName
    - Locale
    - Gender
    - FriendlyName (opcional)
    """
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

    # fallback: se não tiver FriendlyName, usa ShortName
    if "FriendlyName" not in v and "ShortName" in v:
        v["FriendlyName"] = v["ShortName"]

    return v


def _get_voices_file() -> Path:
    # repo root (…/rotas -> .. = root)
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / "edge_voices.json"


def _get_voices() -> List[Dict[str, Any]]:
    voices_path = _get_voices_file()
    if not voices_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Arquivo data/edge_voices.json não encontrado. Adicione o JSON das vozes no repo."
        )

    payload = _load_json_file(voices_path)
    voices = _extract_list(payload)
    voices = [_normalize_voice(v) for v in voices]

    # Ordena para ficar bonito no front (pt primeiro, depois restante)
    def sort_key(x: Dict[str, Any]):
        loc = (x.get("Locale") or "").lower()
        return (0 if loc.startswith("pt-") else 1, (x.get("ShortName") or "").lower())

    voices.sort(key=sort_key)
    return voices


# --------- Routes (aliases para não quebrar o front) ---------

@router.get("/vozes")
@router.get("/api/tts/vozes")
@router.get("/voices")
@router.get("/api/voices")
@router.get("/api/tts/voices")
def listar_vozes():
    """
    Retorna sempre uma LISTA de vozes (JSON).
    Compatível com vários caminhos para evitar quebra no frontend.
    """
    return _get_voices()


@router.get("/api/tts/vozes/ping")
def ping_vozes():
    """
    Endpoint simples pra debug rápido.
    """
    voices_path = _get_voices_file()
    return {
        "ok": True,
        "voices_file_exists": voices_path.exists(),
        "voices_file_path": str(voices_path),
        "count": len(_get_voices()) if voices_path.exists() else 0,
    }
