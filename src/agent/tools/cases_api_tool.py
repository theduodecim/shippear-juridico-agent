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
    """Argumentos para listar causas jurídicas internas."""

    pageSize: int = Field(
        default=100,
        ge=1,
        description="Cantidad de causas a devolver por página.",
    )
    includeArchived: bool = Field(
        default=False,
        description="Incluye causas archivadas cuando es verdadero.",
    )
    updatedSince: str | None = Field(
        default=None,
        description="Fecha ISO 8601 para sincronización incremental de causas actualizadas desde ese momento.",
    )


class CaseDetailInput(BaseModel):
    """Argumentos para obtener el detalle de una causa jurídica interna."""

    id: str = Field(..., description="Identificador de la causa jurídica a consultar.")


class CasesApiTool(BaseTool):
    """Consulta el listado de causas jurídicas internas del sistema."""

    name: str = "get_cases"
    description: str = (
        "Consulta el endpoint interno de causas jurídicas del sistema. Úsala para "
        "buscar o sincronizar expedientes, causas o partes concretas cargadas en "
        "el sistema jurídico interno."
    )
    args_schema: type[BaseModel] = CasesApiInput

    _api_key: str = PrivateAttr(default="")

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa la herramienta leyendo la API key desde la configuración."""

        super().__init__(**kwargs)
        self._api_key = get_config().roxium_agent_key

    def _run(
        self,
        pageSize: int = 100,
        includeArchived: bool = False,
        updatedSince: str | None = None,
    ) -> str:
        """Consulta el listado de causas internas con manejo de errores."""

        if not self._api_key:
            return (
                "No se pudo consultar las causas jurídicas internas: falta configurar "
                "ROXIUM_AGENT_KEY en las variables de entorno."
            )

        params: dict[str, str] = {
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
        pageSize: int = 100,
        includeArchived: bool = False,
        updatedSince: str | None = None,
    ) -> str:
        """Ejecuta la consulta asincrónica delegando la llamada bloqueante."""

        return await asyncio.to_thread(self._run, pageSize, includeArchived, updatedSince)


class CaseDetailTool(BaseTool):
    """Consulta el detalle individual de una causa jurídica interna."""

    name: str = "get_case_detail"
    description: str = (
        "Consulta el detalle de una causa jurídica interna por ID. Úsala cuando "
        "necesites información específica de un expediente o causa concreta del sistema."
    )
    args_schema: type[BaseModel] = CaseDetailInput

    _api_key: str = PrivateAttr(default="")

    def __init__(self, **kwargs: Any) -> None:
        """Inicializa la herramienta leyendo la API key desde la configuración."""

        super().__init__(**kwargs)
        self._api_key = get_config().roxium_agent_key

    def _run(self, id: str) -> str:
        """Consulta el detalle de una causa interna con manejo de errores."""

        if not self._api_key:
            return (
                "No se pudo consultar el detalle de la causa jurídica interna: falta "
                "configurar ROXIUM_AGENT_KEY en las variables de entorno."
            )

        if not id:
            return "No se pudo consultar el detalle de la causa: falta indicar el id."

        return _execute_get_request(
            url=f"{CASES_API_BASE_URL}/{quote(id, safe='')}",
            api_key=self._api_key,
            failure_context=f"consultar el detalle de la causa {id}",
        )

    async def _arun(self, id: str) -> str:
        """Ejecuta la consulta asincrónica delegando la llamada bloqueante."""

        return await asyncio.to_thread(self._run, id)


def _execute_get_request(url: str, api_key: str, failure_context: str) -> str:
    """Ejecuta un GET autenticado y devuelve una respuesta legible."""

    request = Request(
        url=url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        method="GET",
    )

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
    """Formatea JSON cuando es posible; si no, devuelve el cuerpo recibido."""

    if not body:
        return "El endpoint respondió correctamente, pero no devolvió contenido."

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body

    return json.dumps(parsed, ensure_ascii=False, indent=2)


def get_cases_tool() -> CasesApiTool:
    """Devuelve una instancia de la herramienta de listado de causas."""

    return CasesApiTool()


def get_case_detail_tool() -> CaseDetailTool:
    """Devuelve una instancia de la herramienta de detalle de causa."""

    return CaseDetailTool()


cases_api_tool = CasesApiTool()
case_detail_tool = CaseDetailTool()


__all__ = [
    "CaseDetailInput",
    "CaseDetailTool",
    "CasesApiInput",
    "CasesApiTool",
    "case_detail_tool",
    "cases_api_tool",
    "get_case_detail_tool",
    "get_cases_tool",
]
