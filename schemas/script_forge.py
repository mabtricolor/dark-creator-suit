from pydantic import BaseModel


class ScriptForgeRequest(BaseModel):
    canal: str
    tema: str
    publico: str
    tom: str
    tamanho: str  # ex: "500 palavras" ou "3-6 minutos"
    detalhes: str | None = None

    # Dica: mande algo assim pra controlar o tipo de regra
    # ex: "reddit" ou "doc"
    modo: str = "doc"


class ScriptForgeResponse(BaseModel):
    roteiro: str
    modo_usado: str  # "reddit" ou "doc"
