"""Cliente LLM centralizado — Groq via SDK OpenAI-compatível."""
from __future__ import annotations

from openai import OpenAI

from app.config import get_settings

_GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def get_llm_client() -> OpenAI | None:
    """Retorna cliente OpenAI apontando para Groq, ou None se sem chave."""
    settings = get_settings()
    if not settings.groq_api_key:
        return None
    return OpenAI(api_key=settings.groq_api_key, base_url=_GROQ_BASE_URL)


def get_llm_model() -> str:
    return get_settings().groq_model
