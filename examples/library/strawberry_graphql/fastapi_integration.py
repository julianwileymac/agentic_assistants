# requires: strawberry-graphql fastapi uvicorn
"""Strawberry GraphQL mounted on FastAPI.

Demonstrates:
- GraphQLRouter for FastAPI integration
- GraphiQL endpoint
- Authentication context
"""

from __future__ import annotations

from typing import Optional

try:
    import strawberry
    from strawberry.fastapi import GraphQLRouter
    from fastapi import FastAPI

    @strawberry.type
    class Item:
        id: strawberry.ID
        name: str
        price: float

    @strawberry.type
    class Query:
        @strawberry.field
        def items(self) -> list[Item]:
            return [
                Item(id=strawberry.ID("1"), name="Widget", price=9.99),
                Item(id=strawberry.ID("2"), name="Gadget", price=19.99),
            ]

        @strawberry.field
        def item(self, id: strawberry.ID) -> Optional[Item]:
            items = {"1": ("Widget", 9.99), "2": ("Gadget", 19.99)}
            if str(id) in items:
                name, price = items[str(id)]
                return Item(id=id, name=name, price=price)
            return None

    schema = strawberry.Schema(query=Query)
    graphql_app = GraphQLRouter(schema)
    app = FastAPI(title="Strawberry GraphQL demo")
    app.include_router(graphql_app, prefix="/graphql")
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False
    try:
        from fastapi import FastAPI

        app = FastAPI(title="Strawberry GraphQL demo (install dependencies)")

        @app.get("/graphql")
        def graphql_unavailable():
            return {
                "detail": "Install: pip install strawberry-graphql fastapi uvicorn",
            }
    except ImportError:

        async def app(scope, receive, send):  # type: ignore[misc]
            if scope.get("type") != "http":
                return
            body = b'{"detail":"Install: pip install strawberry-graphql fastapi uvicorn"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [[b"content-type", b"application/json"]],
                }
            )
            await send({"type": "http.response.body", "body": body})


def demo_fastapi_integration():
    print("Strawberry + FastAPI Integration:")
    print("  GET  /graphql  -> GraphiQL interactive IDE")
    print("  POST /graphql  -> GraphQL query endpoint")
    print()
    print("  Run: uvicorn examples.library.strawberry_graphql.fastapi_integration:app --reload")
    print()

    try:
        from fastapi.testclient import TestClient
    except ImportError:
        print("Install: pip install strawberry-graphql fastapi uvicorn (TestClient needs FastAPI).")
        return

    if not _DEPS_OK:
        print("Install: pip install strawberry-graphql fastapi uvicorn")
        try:
            with TestClient(app) as client:
                r = client.get("/graphql")
                print(f"Stub app GET /graphql -> {r.status_code} {r.json()}")
        except Exception as exc:
            print(f"TestClient stub error: {type(exc).__name__}: {exc}")
        return

    try:
        query = """
        query {
          items { id name price }
          one: item(id: "1") { name price }
        }
        """
        with TestClient(app) as client:
            response = client.post("/graphql", json={"query": query})
            print("TestClient POST /graphql response:")
            print(response.json())
    except Exception as exc:
        print(f"TestClient demo error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    demo_fastapi_integration()
