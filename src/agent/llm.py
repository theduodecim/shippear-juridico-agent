"""Utilidades para construir modelos de chat compatibles con OpenRouter."""

from langchain_openai import ChatOpenAI

from agent.config import get_config


def get_llm() -> ChatOpenAI:
    """Devuelve un modelo de chat configurado para usar OpenRouter."""

    config = get_config()

    return ChatOpenAI(
        model=config.openrouter_model,
        api_key=config.openrouter_api_key,
        base_url=config.openrouter_base_url,
    )
