# Shippear Jurídico Agent

Proyecto base para construir un sistema de agentes jurídicos con LangChain y LangGraph.

La arquitectura prevista sigue un patrón de **supervisor + sub-agentes delegados**: un agente coordinador recibe la tarea principal, decide qué sub-agentes deben intervenir y delega trabajo especializado, como investigación web o recopilación de contexto.

## Estructura inicial

```text
src/agent/
  config.py
  llm.py
  state.py
  graph.py
  agents/
    coordinator.py
    research_agent.py
  prompts/
    coordinator.py
    research_agent.py
  tools/
    web_search_tool.py
```

Por ahora el repositorio contiene solamente stubs y documentación mínima. La lógica de agentes, prompts, herramientas y grafo se implementará en pasos posteriores.

## Configuración

Copiá `.env.example` a `.env` y completá las claves necesarias:

```bash
cp .env.example .env
```
