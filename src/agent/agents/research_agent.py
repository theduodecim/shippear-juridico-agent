"""Constructor del sub-agente de investigación jurídica."""

from typing import Any

from langchain.agents import create_agent

from agent.llm import get_llm
from agent.prompts.research_agent import RESEARCH_AGENT_SYSTEM_PROMPT
from agent.tools.cases_api_tool import case_detail_tool, cases_api_tool
from agent.tools.web_search_tool import web_search_tool


def build_research_agent() -> Any:
    """Arma el agente investigador jurídico con LLM, prompt y herramientas de investigación."""

    return create_agent(
        model=get_llm(),
        tools=[web_search_tool, cases_api_tool, case_detail_tool],
        system_prompt=RESEARCH_AGENT_SYSTEM_PROMPT,
    )


__all__ = ["build_research_agent"]