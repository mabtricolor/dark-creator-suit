import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ENV: str = os.getenv("ENV", "dev")

    # Gemini
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


settings = Settings()
