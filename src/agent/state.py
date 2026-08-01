"""Estado compartido para consultas jurídicas en agentes LangChain/LangGraph."""

from langchain.agents import AgentState


class LegalQueryState(AgentState):
    """State schema para coordinar una consulta jurídica y sus hallazgos."""

    user_query: str
    research_findings: list[str]


__all__ = ["LegalQueryState"]
