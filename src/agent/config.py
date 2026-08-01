"""Configuración central para variables de entorno del proyecto."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv


DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class AgentConfig:
    """Valores de configuración necesarios para inicializar los agentes."""

    openrouter_api_key: str
    openrouter_model: str = DEFAULT_OPENROUTER_MODEL
    openrouter_base_url: str = OPENROUTER_BASE_URL
    tavily_api_key: str = ""
    roxium_agent_key: str = ""


def get_config() -> AgentConfig:
    """Carga variables de entorno desde `.env` y devuelve la configuración."""

    load_dotenv()

    return AgentConfig(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_model=os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", OPENROUTER_BASE_URL),
        tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
        roxium_agent_key=os.getenv("ROXIUM_AGENT_KEY", ""),
    )
