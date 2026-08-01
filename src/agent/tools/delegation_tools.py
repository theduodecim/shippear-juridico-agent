"""Herramientas para delegar tareas entre agentes LangChain."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field


class ResearchDelegationInput(BaseModel):
    """Entrada para delegar una investigación jurídica al sub-agente."""

    query: str = Field(
        ...,
        description=(
            "Consigna concreta para el investigador jurídico, incluyendo tema, "
            "jurisdicción, fechas, normas, tribunales o hechos relevantes."
        ),
    )


def create_research_delegation_tool(research_agent: Any) -> StructuredTool:
    """Envuelve el agente investigador como tool delegable por el coordinador."""

    def delegate_legal_research(query: str) -> str:
        """Delega una consulta de investigación jurídica y devuelve sus hallazgos."""

        try:
            response = research_agent.invoke({"messages": [("user", query)]})
        except Exception as exc:
            return f"No se pudo delegar la investigación jurídica: {exc}"

        return _stringify_agent_response(response)

    return StructuredTool.from_function(
        func=delegate_legal_research,
        name="delegate_legal_research",
        description=(
            "Delega al sub-agente investigador la búsqueda de normativa, "
            "jurisprudencia, doctrina, fuentes oficiales o noticias legales. "
            "Devuelve hallazgos con las fuentes citadas por el investigador."
        ),
        args_schema=ResearchDelegationInput,
    )


def _stringify_agent_response(response: Any) -> str:
    """Extrae texto útil de una respuesta de agente o runnable de LangChain."""

    if isinstance(response, str):
        return response

    if isinstance(response, dict):
        messages = response.get("messages")
        if messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", None)
            if content:
                return _content_to_text(content)
            if isinstance(last_message, dict) and last_message.get("content"):
                return _content_to_text(last_message["content"])

        output = response.get("output") or response.get("final")
        if output:
            return _content_to_text(output)

    content = getattr(response, "content", None)
    if content:
        return _content_to_text(content)

    return str(response)


def _content_to_text(content: Any) -> str:
    """Normaliza contenido de mensajes LangChain a texto plano."""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    chunks.append(str(text))
            else:
                chunks.append(str(item))
        return "\n".join(chunks)

    return str(content)


__all__ = ["ResearchDelegationInput", "create_research_delegation_tool"]
