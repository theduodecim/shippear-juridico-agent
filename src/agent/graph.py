"""Punto de entrada LangGraph para construir el coordinador jurídico."""

from typing import Any

from agent.agents.coordinator import build_coordinator


async def graph() -> Any:
    """Construye y devuelve el agente coordinador compilado."""

    return build_coordinator()


__all__ = ["graph"]
