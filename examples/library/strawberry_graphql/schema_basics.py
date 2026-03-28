# requires: strawberry-graphql
"""Strawberry GraphQL schema basics: types, inputs, mutations, enums.

Demonstrates:
- @strawberry.type for object types
- @strawberry.input for input types
- @strawberry.mutation for mutations
- @strawberry.enum for enum types
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


def demo_schema():
    try:
        import strawberry

        @strawberry.enum
        class Status(Enum):
            ACTIVE = "active"
            INACTIVE = "inactive"
            ARCHIVED = "archived"

        @strawberry.type
        class User:
            id: strawberry.ID
            name: str
            email: str
            status: Status = Status.ACTIVE

        @strawberry.input
        class CreateUserInput:
            name: str
            email: str
            status: Status = Status.ACTIVE

        @strawberry.type
        class Query:
            @strawberry.field
            def user(self, id: strawberry.ID) -> Optional[User]:
                return User(id=id, name="Alice", email="alice@example.com")

            @strawberry.field
            def users(self) -> list[User]:
                return [
                    User(id=strawberry.ID("1"), name="Alice", email="alice@example.com"),
                    User(id=strawberry.ID("2"), name="Bob", email="bob@example.com"),
                ]

        @strawberry.type
        class Mutation:
            @strawberry.mutation
            def create_user(self, input: CreateUserInput) -> User:
                return User(
                    id=strawberry.ID("3"),
                    name=input.name,
                    email=input.email,
                    status=input.status,
                )

        schema = strawberry.Schema(query=Query, mutation=Mutation)

        result = schema.execute_sync("{ users { id name email status } }")
        print("GraphQL query result:")
        print(f"  {result.data}")
        print()
        print("SDL:")
        print(schema.as_str()[:500])

    except ImportError:
        print("Install: pip install strawberry-graphql")


if __name__ == "__main__":
    demo_schema()
