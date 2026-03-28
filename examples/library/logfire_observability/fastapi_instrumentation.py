# requires: logfire fastapi
"""Logfire FastAPI instrumentation: request/response tracing.

Demonstrates:
- logfire.instrument_fastapi(app)
- Automatic route instrumentation
- Error tracking
"""

from __future__ import annotations

try:
    import logfire

    logfire.configure(send_to_logfire=False)
except ImportError:
    logfire = None

try:
    from fastapi import FastAPI

    app = FastAPI(title="Instrumented API")
    if logfire is not None:
        logfire.instrument_fastapi(app)

    @app.get("/items/{item_id}")
    async def get_item(item_id: int):
        if logfire is not None:
            with logfire.span("fetch-item", item_id=item_id):
                return {"id": item_id, "name": f"Item {item_id}"}
        return {"id": item_id, "name": f"Item {item_id}"}

    @app.post("/items")
    async def create_item(name: str, price: float):
        if logfire is not None:
            with logfire.span("create-item", name=name, price=price):
                return {"id": 1, "name": name, "price": price}
        return {"id": 1, "name": name, "price": price}

    _FASTAPI_OK = True
except ImportError:
    _FASTAPI_OK = False

    async def app(scope, receive, send):  # type: ignore[misc]
        """ASGI stub so `uvicorn ...:app` resolves when FastAPI is not installed."""
        if scope.get("type") != "http":
            return
        body = b'{"detail":"Install: pip install fastapi (and logfire for instrumentation)."}'
        await send(
            {
                "type": "http.response.start",
                "status": 503,
                "headers": [[b"content-type", b"application/json"]],
            }
        )
        await send({"type": "http.response.body", "body": body})


def demo_fastapi_instrumentation():
    print("Logfire + FastAPI instrumentation:")
    print("  Every request/response automatically traced")
    print("  Route, status code, duration, errors captured")
    print("  Custom spans inside handlers for fine-grained tracing")
    print()
    print("  Run: uvicorn examples.library.logfire_observability.fastapi_instrumentation:app --reload")
    print()

    if logfire is None:
        print("Note: logfire not installed — routes still work but spans are no-ops.")
    if not _FASTAPI_OK:
        print("Install: pip install fastapi (and logfire for instrumentation).")
        return

    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            r = client.get("/items/42")
            print(f"TestClient GET /items/42 -> {r.status_code} {r.json()}")
            r2 = client.post("/items", params={"name": "Demo", "price": 9.99})
            print(f"TestClient POST /items -> {r2.status_code} {r2.json()}")
    except Exception as exc:
        print(f"TestClient demo error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    demo_fastapi_instrumentation()
