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


@router.post("/gen-insights", response_model=GenInsightsResponse)
async def gen_insights(req: GenInsightsRequest):
    system = load_prompt("gen_insights_system.txt")
    user = (
        f"Nicho: {req.nicho}\n"
        f"Público: {req.publico}\n"
        f"Tom: {req.tom}\n"
        f"Idioma: {req.idioma}\n"
        f"Gere as ideias no formato exigido."
    )
    client = OpenAICompatClient()

    async def call_llm(sys, usr):
        return await client.chat(sys, usr, temperature=0.8)

    return await enforce_json_model(call_llm, system, user, GenInsightsResponse)


@router.post("/paraphraser", response_model=ParaphraserResponse)
async def paraphraser(req: ParaphraserRequest):
    system = load_prompt("paraphraser_system.txt")
    user = (
        f"IDIOMA DE SAÍDA: {req.idioma_saida}\n\n"
        f"TEXTO ORIGINAL:\n{req.texto_original}\n\n"
        f"REGRAS EXTRAS:\n{req.regras_extras or 'nenhuma'}\n\n"
        f"Entregue o texto final pronto para TTS."
    )
    client = GeminiClient()
    out = await client.generate(system, user, temperature=0.6)
    return ParaphraserResponse(texto_transmutado=out)


@router.post("/script-forge", response_model=ScriptForgeResponse)
async def script_forge(req: ScriptForgeRequest):
    system = load_prompt("script_forge_system.txt")
    user = (
        f"CANAL: {req.canal}\n"
        f"TEMA: {req.tema}\n"
        f"PÚBLICO: {req.publico}\n"
        f"TOM: {req.tom}\n"
        f"DURAÇÃO: {req.duracao_aprox}\n"
        f"DETALHES:\n{req.detalhes or 'nenhum'}\n\n"
        f"Crie o roteiro final."
    )
    client = GeminiClient()
    out = await client.generate(system, user, temperature=0.7)
    return ScriptForgeResponse(roteiro=out)


@router.post("/meta-seo", response_model=MetaSEOResponse)
async def meta_seo(req: MetaSEORequest):
    system = load_prompt("meta_seo_system.txt")
    user = (
        f"CANAL: {req.canal}\n\n"
        f"HISTÓRIA:\n{req.historia}\n\n"
        f"OBSERVAÇÕES:\n{req.observacoes or 'nenhuma'}\n\n"
        f"Entregue o resultado completo."
    )
    client = GeminiClient()
    out = await client.generate(system, user, temperature=0.55)
    return MetaSEOResponse(seo_result=out)


@router.post("/thumb-maker", response_model=ThumbMakerResponse)
async def thumb_maker(req: ThumbMakerRequest):
    system = load_prompt("thumb_maker_system.txt")
    user = (
        f"TITLE (PT-BR): {req.titulo}\n"
        f"SCRIPT SUMMARY (PT-BR): {req.resumo}\n"
        f"VISUAL STYLE: {req.estilo_visual}\n"
        f"EXACT OVERLAY TEXT (must be verbatim, PT-BR): {req.texto_overlay_exato}\n"
        f"RESTRICTIONS: {req.restricoes or 'none'}\n\n"
        f"Return 3 concepts as JSON in the required format."
    )

    client = GeminiClient()

    async def call_llm(sys, usr):
        return await client.generate(sys, usr, temperature=0.8)

    return await enforce_json_model(call_llm, system, user, ThumbMakerResponse)
