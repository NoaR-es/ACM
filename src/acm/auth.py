"""Autenticación HTTP de ACM (EPIC-20, ADR-017).

`BearerAuth` envuelve una aplicación ASGI: exige `Authorization: Bearer acm_…` en cada petición HTTP, valida el token
contra la base (revocación inmediata) y deja la identidad en variables de contexto que leen las herramientas MCP.
Una petición sin credencial válida recibe 401 y no llega a la aplicación; el intento queda auditado (US-20.02 CA-04).

Comprobado en SPRINT-004: la variable de contexto de la petición llega a la herramienta MCP (también dentro del hilo
de trabajo) sin mezclarse entre peticiones concurrentes (0 mezclas en 200 llamadas de 8 identidades).
"""

from __future__ import annotations

import contextvars
import json
import time

import anyio
from starlette.types import ASGIApp, Receive, Scope, Send

from acm.domain.audit import AuditService
from acm.domain.errors import AcmError, Unauthenticated
from acm.domain.identity import PREFIX_SHOWN, IdentityService

current_principal: contextvars.ContextVar[str | None] = contextvars.ContextVar("acm_principal", default=None)
current_token: contextvars.ContextVar[str | None] = contextvars.ContextVar("acm_token", default=None)
ANONYMOUS = "(anonymous)"


def request_principal() -> str:
    """Principal de la petición HTTP en curso. Fuera de una petición autenticada no hay identidad."""
    principal = current_principal.get()
    if principal is None:
        raise Unauthenticated("petición sin identidad autenticada")
    return principal


def request_token() -> str | None:
    return current_token.get()


class BearerAuth:
    def __init__(self, app: ASGIApp, identity: IdentityService, audit: AuditService):
        self.app = app
        self.identity = identity
        self.audit = audit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        header = next((v.decode("latin-1") for k, v in scope["headers"] if k.lower() == b"authorization"), "")
        secret = header[7:].strip() if header.lower().startswith("bearer ") else ""
        start = time.perf_counter()
        try:
            principal, token_id = await anyio.to_thread.run_sync(self.identity.authenticate, secret)
        except AcmError as exc:
            await anyio.to_thread.run_sync(self._audit_rejection, scope, secret, exc, start)
            await _reject(send, exc)
            return
        p_token, t_token = current_principal.set(principal), current_token.set(token_id)
        try:
            await self.app(scope, receive, send)
        finally:
            current_principal.reset(p_token)
            current_token.reset(t_token)

    def _audit_rejection(self, scope: Scope, secret: str, exc: AcmError, start: float) -> None:
        self.audit.record(
            principal=ANONYMOUS,
            operation="http:auth",
            arguments={"method": scope.get("method"), "path": scope.get("path"), "token_prefix": secret[:PREFIX_SHOWN]},
            status="error",
            duration_ms=(time.perf_counter() - start) * 1000,
            error=str(exc),
        )


async def _reject(send: Send, exc: AcmError) -> None:
    body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
    headers: list[tuple[bytes, bytes]] = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(body)).encode()),
        (b"www-authenticate", b'Bearer realm="acm"'),
    ]
    await send({"type": "http.response.start", "status": 401, "headers": headers})
    await send({"type": "http.response.body", "body": body})
