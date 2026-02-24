import httpx
from .config import settings


class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY não configurada nas variáveis de ambiente.")
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL

    async def generate(self, system: str, user: str, temperature: float = 0.7) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        params = {"key": self.api_key}

        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(url, params=params, json=payload)
            r.raise_for_status()
            data = r.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return ""

        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()
