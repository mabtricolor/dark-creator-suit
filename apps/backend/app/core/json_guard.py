import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def extract_json_object(text: str) -> str:
    """
    Tenta extrair o primeiro objeto JSON {...} de uma resposta que pode vir com texto extra.
    """
    text = text.strip()

    # Se já parece JSON puro:
    if text.startswith("{") and text.endswith("}"):
        return text

    # Tenta pegar o maior bloco {...}
    match = re.search(r"\{.*\}", text, re.S)
    if match:
        return match.group(0).strip()

    return text


def parse_json_as_model(text: str, model: Type[T]) -> T:
    raw = extract_json_object(text)
    data = json.loads(raw)
    return model.model_validate(data)


async def enforce_json_model(call_llm, system: str, user: str, model: Type[T], max_retries: int = 2) -> T:
    """
    Chama LLM e garante que retorna JSON compatível com um model Pydantic.
    """
    last_err = None
    cur_user = user

    for _ in range(max_retries + 1):
        out = await call_llm(system, cur_user)
        try:
            return parse_json_as_model(out, model)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            # “Reprimenda” para corrigir formato
            cur_user = (
                user
                + "\n\nIMPORTANTE: Sua resposta anterior estava fora do formato. "
                  "Retorne APENAS um objeto JSON válido, sem texto extra, sem markdown."
            )

    raise ValueError(f"Falha ao obter JSON válido do modelo. Erro: {last_err}")
