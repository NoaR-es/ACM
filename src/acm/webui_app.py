"""Interfaz web de ACM (SPRINT-007, ADR-019): los archivos compilados de `web/` servidos en `/`.

Cabeceras de seguridad en cada respuesta: CSP que solo permite recursos propios y conexiones (fetch y WebSocket) al
mismo host, `nosniff`, sin referrer y sin poder incrustarse en otros sitios. El Markdown se sanea en el cliente
(DOMPurify) y la CSP impide ejecutar scripts inyectados aunque el saneado fallara.
"""

from __future__ import annotations

from pathlib import Path

from starlette.staticfiles import StaticFiles
from starlette.types import Message, Receive, Scope, Send

WEBUI_DIR = Path(__file__).parent / "webui"


class SecureStatic:
    def __init__(self, directory: Path = WEBUI_DIR):
        self.static = StaticFiles(directory=directory, html=True)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        host = next((v.decode("latin-1") for k, v in scope.get("headers", []) if k == b"host"), "")
        csp = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
            f"connect-src 'self' ws://{host} wss://{host}; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'"
        )

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers += [
                    (b"content-security-policy", csp.encode("latin-1")),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                ]
                message["headers"] = headers
            await send(message)

        await self.static(scope, receive, send_with_headers)


def webui_available() -> bool:
    return (WEBUI_DIR / "index.html").is_file()
