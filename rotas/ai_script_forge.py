from fastapi import APIRouter, HTTPException

from core.prompt_loader import load_prompt, fill_template
from core.llm_gemini import GeminiClient
from schemas.script_forge import ScriptForgeRequest, ScriptForgeResponse

router = APIRouter(prefix="/api/ai", tags=["AI"])


def escolher_rules(modo: str) -> tuple[str, str]:
    modo_norm = (modo or "").strip().lower()

    if modo_norm in ("reddit", "relato", "relatos", "porao", "porão", "reddit/relatos"):
        return "reddit", load_prompt("script_forge_rules_reddit.txt")

    # padrão: doc/listas/mistério
    return "doc", load_prompt("script_forge_rules_doc.txt")


@router.post("/script-forge", response_model=ScriptForgeResponse)
async def script_forge(req: ScriptForgeRequest):
    try:
        system_template = load_prompt("script_forge_system.txt")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Arquivo prompts/script_forge_system.txt não encontrado.")

    modo_usado, rules = escolher_rules(req.modo)

    system = fill_template(
        system_template,
        {
            "CANAL": req.canal,
            "TAMANHO": req.tamanho,
            "CANAL_RULES": rules,
        },
    )

    # O "user" é onde você coloca o briefing do vídeo
    user = (
        f"CANAL: {req.canal}\n"
        f"TEMA: {req.tema}\n"
        f"PÚBLICO: {req.publico}\n"
        f"TOM: {req.tom}\n"
        f"TAMANHO: {req.tamanho}\n\n"
        f"DETALHES:\n{req.detalhes or 'nenhum'}\n\n"
        "Crie o roteiro final agora."
    )

    client = GeminiClient()
    roteiro = await client.generate(system=system, user=user, temperature=0.75)

    # Garantia mínima: nunca devolver vazio
    if not roteiro.strip():
        raise HTTPException(status_code=502, detail="O modelo retornou vazio. Tente novamente.")

    return ScriptForgeResponse(roteiro=roteiro, modo_usado=modo_usado)
