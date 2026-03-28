# requires: strawberry-graphql
# optional: fastapi uvicorn (for module-level `app` and TestClient)
"""Strawberry DataLoader for batching and caching N+1 queries.

Demonstrates:
- DataLoader pattern to batch database requests
- Cache within a single request
- Integration with Strawberry resolvers
"""

from __future__ import annotations

import asyncio

try:
    import strawberry
    from strawberry.dataloader import DataLoader

    AUTHOR_DB = {
        "1": {"id": "1", "name": "Alice"},
        "2": {"id": "2", "name": "Bob"},
    }

    async def load_authors(keys: list[str]) -> list[dict]:
        """Batch load: called once for all requested author IDs."""
        print(f"  Batch loading authors: {keys}")
        return [AUTHOR_DB.get(k, {"id": k, "name": "Unknown"}) for k in keys]

    @strawberry.type
    class Author:
        id: strawberry.ID
        name: str

    @strawberry.type
    class Book:
        title: str
        author_id: strawberry.ID

        @strawberry.field
        async def author(self, info: strawberry.types.Info) -> Author:
            loader: DataLoader = info.context["author_loader"]
            data = await loader.load(str(self.author_id))
            return Author(id=strawberry.ID(data["id"]), name=data["name"])

    @strawberry.type
    class Query:
        @strawberry.field
        async def books(self) -> list[Book]:
            return [
                Book(title="Book A", author_id=strawberry.ID("1")),
                Book(title="Book B", author_id=strawberry.ID("2")),
            ]

    @strawberry.type
    class SyncProbe:
        """Minimal sync type so execute_sync can run without an event loop."""

        @strawberry.field
        def ping(self) -> str:
            return "dataloaders-ok"

    _schema = strawberry.Schema(query=Query)
    _sync_schema = strawberry.Schema(query=SyncProbe)
    _STRAWBERRY_OK = True
except ImportError:
    _STRAWBERRY_OK = False
    _schema = None
    _sync_schema = None

try:
    if not _STRAWBERRY_OK or _schema is None:
        raise ImportError("strawberry schema not available")
    from strawberry.fastapi import GraphQLRouter
    from fastapi import FastAPI

    async def get_graphql_context() -> dict:
        return {"author_loader": DataLoader(load_fn=load_authors)}

    _graphql_router = GraphQLRouter(_schema, context_getter=get_graphql_context)
    app = FastAPI(title="Strawberry DataLoader demo")
    app.include_router(_graphql_router, prefix="/graphql")
    _FASTAPI_OK = True
except ImportError:
    _FASTAPI_OK = False
    try:
        from fastapi import FastAPI

        app = FastAPI(title="Strawberry DataLoader (install strawberry-graphql)")

        @app.get("/graphql")
        def _graphql_stub():
            return {"detail": "Install: pip install strawberry-graphql [fastapi]"}
    except ImportError:

        async def app(scope, receive, send):  # type: ignore[misc]
            if scope.get("type") != "http":
                return
            body = b'{"detail":"Install: pip install strawberry-graphql"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({"type": "http.response.body", "body": body})


def demo_dataloaders():
    print("DataLoader Pattern:")
    print("  Without DataLoader: N+1 queries for N books")
    print("  With DataLoader: 1 batch query for all authors")
    print()
    print("  Setup in FastAPI context:")
    print("  async def get_context():")
    print("      return {'author_loader': DataLoader(load_fn=load_authors)}")
    print()

    if not _STRAWBERRY_OK:
        print("Install: pip install strawberry-graphql")
        return

    query = """
    query {
      books {
        title
        author { name }
      }
    }
    """

    async def _run() -> None:
        assert _schema is not None
        result = await _schema.execute(
            query,
            context_value={"author_loader": DataLoader(load_fn=load_authors)},
        )
        print("schema.execute() (async) result:")
        print(result)

    try:
        assert _sync_schema is not None
        probe = _sync_schema.execute_sync("query { ping }")
        print("schema.execute_sync() on a sync-only field (probe):")
        print(probe)
    except Exception as exc:
        print(f"execute_sync probe error: {type(exc).__name__}: {exc}")

    try:
        asyncio.run(_run())
    except Exception as exc:
        print(f"Async execute demo error: {type(exc).__name__}: {exc}")

    if not _FASTAPI_OK:
        print()
        print("Optional: pip install fastapi uvicorn for module-level `app` and TestClient demo.")
        return

    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            resp = client.post("/graphql", json={"query": query})
            print("TestClient POST /graphql:")
            print(resp.status_code, resp.json())
    except Exception as exc:
        print(f"TestClient demo error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    demo_dataloaders()
