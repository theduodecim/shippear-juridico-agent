"""Constructor del agente coordinador jurídico."""

from typing import Any

from langchain.agents import create_agent

from agent.agents.research_agent import build_research_agent
from agent.llm import get_llm
from agent.prompts.coordinator import COORDINATOR_SYSTEM_PROMPT
from agent.state import LegalQueryState
from agent.tools.delegation_tools import create_research_delegation_tool


def build_coordinator(research_agent: Any | None = None) -> Any:
    """Arma el agente coordinador con delegación al investigador jurídico."""

    research_agent = research_agent or build_research_agent()
    research_delegation_tool = create_research_delegation_tool(research_agent)

    return create_agent(
        model=get_llm(),
        tools=[research_delegation_tool],
        system_prompt=COORDINATOR_SYSTEM_PROMPT,
        state_schema=LegalQueryState,
    )


__all__ = ["build_coordinator"]
