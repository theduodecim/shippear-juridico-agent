# ⚖️ Shippear Jurídico Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-multi--agent-green)

Agente jurídico desarrollado durante la **Hackathon de Shippear**, como parte de una solución integral para la gestión jurídica.

El proyecto utiliza **LangChain** y **LangGraph** para implementar una arquitectura basada en un supervisor y sub-agentes especializados.

---

## 🧠 Arquitectura

El sistema está diseñado alrededor de un agente coordinador que recibe la tarea principal y decide qué agentes especializados deben intervenir.

```
                    ┌──────────────────┐
                    │  Agente          │
                    │  Coordinador     │
                    │   (Supervisor)   │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
        ┌────────▼────────┐    ┌────────▼────────┐
        │ Research Agent  │    │  Otros agentes  │
        │ Investigación   │    │ especializados  │
        └─────────────────┘    └─────────────────┘
```

---

## 🛠️ Tecnologías

- Python
- LangChain
- LangGraph
- LLMs
- Arquitectura multi-agente

---

## 📁 Estructura

```
.
├── frontend/              # Interfaz de usuario
├── src/agent/
│   ├── config.py
│   ├── llm.py
│   ├── state.py
│   ├── graph.py
│   ├── agents/
│   │   ├── coordinator.py
│   │   └── research_agent.py
│   ├── prompts/
│   │   ├── coordinator.py
│   │   └── research_agent.py
│   └── tools/
│       └── web_search_tool.py
├── langgraph.json          # Configuración del grafo de LangGraph
├── pyproject.toml          # Dependencias (Poetry / uv)
├── .env.example
└── LICENSE
```

---

## ⚙️ Instalación y configuración

### 1. Variables de entorno

Copiá el archivo de variables de entorno y completá las claves necesarias:

```bash
cp .env.example .env
```

> ⚠️ **No subas credenciales ni API keys al repositorio.**

### 2. Dependencias

El proyecto gestiona dependencias con **Poetry** o **uv** (ambos lockfiles están incluidos):

```bash
# Con Poetry
poetry install

# o con uv
uv sync
```

### 3. Frontend

El proyecto incluye una interfaz en `frontend/`. Consultá su propio README (si existe) para instrucciones específicas de instalación y ejecución.

---

## 🚀 Contexto

Este repositorio forma parte del proyecto desarrollado durante la **Hackathon de Shippear**, donde la solución completa quedó entre los **6 mejores proyectos**.

El objetivo de este componente es incorporar capacidades de IA y agentes especializados a la plataforma de gestión jurídica.

---

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Ver el archivo [LICENSE](LICENSE) para más detalles.
