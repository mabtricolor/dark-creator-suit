from pydantic import BaseModel, Field


class GenInsightsRequest(BaseModel):
    nicho: str
    publico: str
    tom: str = "dark"
    idioma: str = "pt-BR"


class InsightIdea(BaseModel):
    titulo: str
    gancho: str
    promessa: str
    estrutura: str


class GenInsightsResponse(BaseModel):
    ideias: list[InsightIdea]


class ParaphraserRequest(BaseModel):
    idioma_saida: str = "pt-BR"
    texto_original: str
    regras_extras: str | None = None


class ParaphraserResponse(BaseModel):
    texto_transmutado: str


class ScriptForgeRequest(BaseModel):
    canal: str
    tema: str
    publico: str
    tom: str
    duracao_aprox: str = "3-6 minutos"
    detalhes: str | None = None


class ScriptForgeResponse(BaseModel):
    roteiro: str


class MetaSEORequest(BaseModel):
    canal: str
    historia: str
    observacoes: str | None = None


class MetaSEOResponse(BaseModel):
    seo_result: str


class ThumbMakerRequest(BaseModel):
    titulo: str
    resumo: str
    estilo_visual: str = "ultra-realista, cinematográfico"
    texto_overlay_exato: str
    restricoes: str | None = None


class ThumbConcept(BaseModel):
    nome: str = Field(..., description="Nome curto do conceito")
    prompt_gringo: str = Field(..., description="Prompt completo em inglês")
    overlay_text: str = Field(..., description="Texto na thumbnail (PT-BR, exato)")
    notas: str = Field(..., description="Notas rápidas pro editor")


class ThumbMakerResponse(BaseModel):
    capas: list[ThumbConcept]
