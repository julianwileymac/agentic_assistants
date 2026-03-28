# requires: strawberry-graphql
"""Strawberry custom resolvers and async resolvers.

Demonstrates:
- @strawberry.field with custom resolver functions
- Async resolvers
- Resolver arguments and info context
"""

from __future__ import annotations

from typing import Optional


def demo_resolvers():
    try:
        import strawberry
        from strawberry.types import Info

        @strawberry.type
        class Book:
            id: strawberry.ID
            title: str
            author: str
            rating: float

        BOOKS_DB = [
            Book(id=strawberry.ID("1"), title="Python Mastery", author="Jane", rating=4.8),
            Book(id=strawberry.ID("2"), title="Async Patterns", author="Bob", rating=4.5),
            Book(id=strawberry.ID("3"), title="GraphQL Guide", author="Jane", rating=4.9),
        ]

        @strawberry.type
        class Query:
            @strawberry.field
            def book(self, id: strawberry.ID) -> Optional[Book]:
                """Resolver with arguments."""
                return next((b for b in BOOKS_DB if b.id == id), None)

            @strawberry.field
            def books_by_author(self, author: str) -> list[Book]:
                return [b for b in BOOKS_DB if b.author.lower() == author.lower()]

            @strawberry.field
            def top_rated(self, min_rating: float = 4.5) -> list[Book]:
                return sorted(
                    [b for b in BOOKS_DB if b.rating >= min_rating],
                    key=lambda b: b.rating,
                    reverse=True,
                )

        schema = strawberry.Schema(query=Query)

        result = schema.execute_sync('{ topRated(minRating: 4.7) { title rating } }')
        print("Custom resolver result:")
        print(f"  {result.data}")

    except ImportError:
        print("Install: pip install strawberry-graphql")


if __name__ == "__main__":
    demo_resolvers()
