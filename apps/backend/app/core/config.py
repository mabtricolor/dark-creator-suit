from pydantic import BaseModel
import os


class Settings(BaseModel):
    APP_NAME: str = "Dark Creator Suite API"
    ENV: str = os.getenv("ENV", "dev")

    # LLM Keys
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # OpenAI-compatible settings (Groq / OpenRouter / etc.)
    OPENAI_COMPAT_BASE_URL: str = os.getenv("OPENAI_COMPAT_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Gemini model
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()
