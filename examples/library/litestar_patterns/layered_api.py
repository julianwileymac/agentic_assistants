# requires: litestar>=2

"""
Structured Litestar apps: controllers, guards, dependencies, and middleware.

Patterns illustrated:

- ``Controller`` groups related paths under a shared prefix and configuration.
- ``dependencies`` + ``Provide`` inject per-request or singleton values (settings,
  DB sessions, feature flags).
- ``guards`` centralize authorization before the handler body executes.
- ``ASGIMiddleware`` implements cross-cutting ASGI concerns (logging, tracing).

The ``TestClient`` exercises the stack without starting a real server.
"""

from __future__ import annotations

from litestar import Controller, Litestar, Request, Router, get
from litestar.di import Provide
from litestar.enums import ScopeType
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import ASGIMiddleware
from litestar.testing import TestClient
from litestar.types import ASGIApp, Receive, Scope, Send


async def settings_provider() -> dict[str, str]:
    """Fake async settings — replace with ``BaseSettings`` + caching in real apps."""
    return {"greeting": "hello"}


async def auth_guard(request: Request, _: object) -> None:
    """Reject requests missing a trivial bearer token."""
    auth = request.headers.get("authorization", "")
    if auth != "Bearer demo-token":
        raise NotAuthorizedException("missing token")


class RequestLoggingMiddleware(ASGIMiddleware):
    """Logs the HTTP method for each request (minimal ASGI middleware example)."""

    scopes = (ScopeType.HTTP,)

    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp) -> None:
        if scope["type"] == "http":
            method = scope.get("method", "")
            path = scope.get("path", "")
            print(f"[middleware] {method} {path}")
        await next_app(scope, receive, send)


class HelloController(Controller):
    path = "/hello"
    tags = ["demo"]
    dependencies = {"settings": Provide(settings_provider)}
    guards = [auth_guard]

    @get("/")
    async def greet(self, settings: dict[str, str]) -> dict[str, str]:
        return {"message": settings["greeting"]}


@get("/public")
async def public() -> dict[str, str]:
    return {"message": "open"}


@get("/health", dependencies={"settings": Provide(settings_provider)})
async def health(settings: dict[str, str]) -> dict[str, str]:
    """Simple route-level dependency injection without a controller."""
    return {"status": "ok", "greeting": settings["greeting"]}


# --- Design notes -----------------------------------------------------------
# Guards should stay free of heavy I/O; offload policy checks to services when needed.
# Middleware instances must be stateless — stash per-request data on ``scope`` or contextvars.
# Router nesting mirrors URL namespaces and keeps OpenAPI tags consistent.
# ---------------------------------------------------------------------------


def create_app() -> Litestar:
    router = Router(path="/api", route_handlers=[HelloController, public, health])
    return Litestar(
        route_handlers=[router],
        # ``ASGIMiddleware`` subclasses are *instances*; each call returns an ASGI wrapper.
        middleware=[RequestLoggingMiddleware()],
    )


def main() -> None:
    app = create_app()
    with TestClient(app=app) as client:
        ok = client.get("/api/hello", headers={"authorization": "Bearer demo-token"})
        print("guarded:", ok.status_code, ok.json())
        denied = client.get("/api/hello")
        print("no token:", denied.status_code)
        print("public:", client.get("/api/public").json())
        print("health:", client.get("/api/health").json())


if __name__ == "__main__":
    main()
