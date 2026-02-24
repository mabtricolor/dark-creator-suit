import httpx
from .config import settings


class OpenAICompatClient:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY não configurada.")
        self.base_url = settings.OPENAI_COMPAT_BASE_URL.rstrip("/")
        self.api_key = settings.GROQ_API_KEY

    async def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        return data["choices"][0]["message"]["content"]
