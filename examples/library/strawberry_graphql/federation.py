# requires: strawberry-graphql
"""Strawberry Federation for microservices GraphQL.

Demonstrates:
- @strawberry.federation.type for federated types
- Extending types across services
- Key fields for entity resolution
"""

from __future__ import annotations


def demo_federation():
    try:
        import strawberry

        @strawberry.federation.type(keys=["id"])
        class User:
            id: strawberry.ID
            name: str
            email: str

            @classmethod
            def resolve_reference(cls, id: strawberry.ID) -> "User":
                return User(id=id, name=f"User_{id}", email=f"user_{id}@example.com")

        @strawberry.federation.type(keys=["id"])
        class Review:
            id: strawberry.ID
            body: str
            author: User

        @strawberry.type
        class Query:
            @strawberry.field
            def users(self) -> list[User]:
                return [User(id=strawberry.ID("1"), name="Alice", email="alice@example.com")]

        schema = strawberry.Schema(query=Query, enable_federation_2=True)

        print("Strawberry Federation:")
        print("  Users service provides User type with key 'id'")
        print("  Reviews service extends User with reviews")
        print("  Apollo Gateway/Router composes the supergraph")
        print()
        print("  Federation SDL (first 300 chars):")
        print(f"  {schema.as_str()[:300]}")

    except ImportError:
        print("Install: pip install strawberry-graphql")


if __name__ == "__main__":
    demo_federation()
