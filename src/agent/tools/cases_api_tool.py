"""Herramientas LangChain para consultar causas jurídicas internas."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from agent.config import get_config


CASES_API_BASE_URL = "https://backend-sistema-juridico-production.up.railway.app/api/agent/cases"
REQUEST_TIMEOUT_SECONDS = 20


class CasesApiInput(BaseModel):
    page: int = Field(default=1, ge=1, description="Número de página a consultar.")
    pageSize: int = Field(default=5, ge=1, le=10, description="Cantidad de causas a devolver por página (máximo 10).")
    includeArchived: bool = Field(default=False, description="Incluye causas archivadas cuando es verdadero.")
    updatedSince: str | None = Field(default=None, description="Fecha ISO 8601 para sincronización incremental.")


class CaseDetailInput(BaseModel):
    id: str = Field(..., description="Identificador de la causa jurídica a consultar.")


class CasesApiTool(BaseTool):
    name: str = "get_cases"
    description: str = (
        "Consulta el endpoint interno de causas jurídicas del sistema. Úsala para "
        "buscar o sincronizar expedientes, causas o partes concretas cargadas en "
        "el sistema jurídico interno. Por defecto trae pocas causas (5) para evitar "
        "respuestas demasiado grandes; aumentá pageSize solo si el usuario lo pide "
        "explícitamente."
    )
    args_schema: type[BaseModel] = CasesApiInput
    _api_key: str = PrivateAttr(default="")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key = get_config().roxium_agent_key

    def _run(
        self,
        page: int = 1,
        pageSize: int = 5,
        includeArchived: bool = False,
        updatedSince: str | None = None,
    ) -> str:
        if not self._api_key:
            return "No se pudo consultar las causas jurídicas internas: falta configurar ROXIUM_AGENT_KEY."
        params: dict[str, str] = {
            "page": str(page),
            "pageSize": str(pageSize),
            "includeArchived": str(includeArchived).lower(),
        }
        if updatedSince:
            params["updatedSince"] = updatedSince
        return _execute_get_request(
            url=f"{CASES_API_BASE_URL}?{urlencode(params)}",
            api_key=self._api_key,
            failure_context="consultar las causas jurídicas internas",
        )

    async def _arun(
        self,
        page: int = 1,
        pageSize: int = 5,
        includeArchived: bool = False,
        updatedSince: str | None = None,
    ) -> str:
        return await asyncio.to_thread(self._run, page, pageSize, includeArchived, updatedSince)


class CaseDetailTool(BaseTool):
    name: str = "get_case_detail"
    description: str = (
        "Consulta el detalle de una causa jurídica interna por ID. Úsala cuando "
        "necesites información específica de un expediente o causa concreta del sistema."
    )
    args_schema: type[BaseModel] = CaseDetailInput
    _api_key: str = PrivateAttr(default="")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._api_key = get_config().roxium_agent_key

    def _run(self, id: str) -> str:
        if not self._api_key:
            return "No se pudo consultar el detalle de la causa jurídica interna: falta configurar ROXIUM_AGENT_KEY."
        if not id:
            return "No se pudo consultar el detalle de la causa: falta indicar el id."
        return _execute_get_request(
            url=f"{CASES_API_BASE_URL}/{quote(id, safe='')}",
            api_key=self._api_key,
            failure_context=f"consultar el detalle de la causa {id}",
        )

    async def _arun(self, id: str) -> str:
        return await asyncio.to_thread(self._run, id)


def _execute_get_request(url: str, api_key: str, failure_context: str) -> str:
    request = Request(url=url, headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        suffix = f" Respuesta: {details}" if details else ""
        return f"No se pudo {failure_context}: el endpoint respondió HTTP {exc.code}.{suffix}"
    except TimeoutError:
        return f"No se pudo {failure_context}: la solicitud agotó el tiempo de espera."
    except URLError as exc:
        return f"No se pudo {failure_context}: error de conexión ({exc.reason})."
    except Exception as exc:
        return f"No se pudo {failure_context}: {exc}"
    return _format_json_response(body)


def _format_json_response(body: str) -> str:
    if not body:
        return "El endpoint respondió correctamente, pero no devolvió contenido."
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body
    return json.dumps(parsed, ensure_ascii=False, indent=2)


cases_api_tool = CasesApiTool()
case_detail_tool = CaseDetailTool()

__all__ = ["CaseDetailInput", "CaseDetailTool", "CasesApiInput", "CasesApiTool", "case_detail_tool", "cases_api_tool"]
