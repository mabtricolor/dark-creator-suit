from fastapi import APIRouter

from ..core.prompt_loader import load_prompt
from ..core.llm_openai_compat import OpenAICompatClient
from ..core.llm_gemini import GeminiClient
from ..core.json_guard import enforce_json_model

from ..schemas.ai import (
    GenInsightsRequest, GenInsightsResponse,
    ParaphraserRequest, ParaphraserResponse,
    ScriptForgeRequest, ScriptForgeResponse,
    MetaSEORequest, MetaSEOResponse,
    ThumbMakerRequest, ThumbMakerResponse,
)

router = APIRouter(prefix="/api/ai", tags=["AI"])


@app.get("/health")
def health():
    return {"ok": True, "app": settings.APP_NAME}
