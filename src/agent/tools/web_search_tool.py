"""Herramienta LangChain para búsquedas web jurídicas con Tavily."""

from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from tavily import TavilyClient

from agent.config import get_config


class WebSearchInput(BaseModel):
    """Argumentos de entrada para la búsqueda web jurídica."""

    query: str = Field(
        ...,
        description=(
            "Consulta de búsqueda. Debe enfocarse en normativa, jurisprudencia, "
            "doctrina, organismos oficiales o noticias legales relevantes."
        ),
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Cantidad máxima de resultados a devolver.",
    )


class WebSearchTool(BaseTool):
    """Busca información jurídica actualizada en la web mediante Tavily."""

    name: str = "web_search"
    description: str = (
        "Usa Tavily para buscar en la web normativa, jurisprudencia, doctrina, "
        "fuentes oficiales o noticias legales actualizadas. Devuelve un resumen "
        "con títulos, URLs y fragmentos útiles para investigación jurídica."
    )
    args_schema: type[BaseModel] = WebSearchInput

    _client: TavilyClient | None = PrivateAttr(default=None)
    _api_key: str = PrivateAttr(default="")

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa la herramienta leyendo la API key desde la configuración."""

        super().__init__(**kwargs)
        config = get_config()
        self._api_key = config.tavily_api_key
        if self._api_key:
            self._client = TavilyClient(api_key=self._api_key)

    def _run(self, query: str, max_results: int = 5) -> str:
        """Ejecuta una búsqueda web sincrónica con manejo de errores."""

        if not self._api_key or self._client is None:
            return (
                "No se pudo ejecutar la búsqueda web: falta configurar "
                "TAVILY_API_KEY en las variables de entorno."
            )

        try:
            response = self._client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
            )
        except Exception as exc:
            return f"No se pudo ejecutar la búsqueda web con Tavily: {exc}"

        return self._format_response(response)

    async def _arun(self, query: str, max_results: int = 5) -> str:
        """Ejecuta una búsqueda web asincrónica delegando la llamada bloqueante."""

        return await asyncio.to_thread(self._run, query, max_results)

    @staticmethod
    def _format_response(response: dict[str, Any]) -> str:
        """Convierte la respuesta de Tavily en texto legible para el agente."""

        answer = response.get("answer")
        results = response.get("results") or []

        if not answer and not results:
            return "Tavily no devolvió resultados para la búsqueda solicitada."

        sections: list[str] = []
        if answer:
            sections.append(f"Resumen de Tavily:\n{answer}")

        if results:
            formatted_results = []
            for index, result in enumerate(results, start=1):
                title = result.get("title") or "Sin título"
                url = result.get("url") or "Sin URL"
                content = result.get("content") or "Sin fragmento disponible."
                score = result.get("score")
                score_text = f"\n   Relevancia: {score:.2f}" if isinstance(score, float) else ""
                formatted_results.append(
                    f"{index}. {title}\n   URL: {url}{score_text}\n   Fragmento: {content}"
                )
            sections.append("Resultados:\n" + "\n\n".join(formatted_results))

        return "\n\n".join(sections)


def get_web_search_tool() -> WebSearchTool:
    """Devuelve una instancia de la herramienta de búsqueda web."""

    return WebSearchTool()


web_search_tool = WebSearchTool()


__all__ = ["WebSearchInput", "WebSearchTool", "get_web_search_tool", "web_search_tool"]
