# requires: sqlmodel sqlalchemy pydantic
"""SQLModel trade-offs: unified vs split model approaches.

Demonstrates:
- Approach A: SQLModel single class (simple, less control)
- Approach B: Separate Pydantic + SQLAlchemy (more control, more code)
- Guidance on when to use each
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def demo_approach_a():
    """SQLModel unified approach."""
    try:
        from sqlmodel import SQLModel, Field

        class UserBase(SQLModel):
            username: str = Field(index=True, unique=True)
            email: str = Field(unique=True)
            full_name: str = ""

        class User(UserBase, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
            password_hash: str = ""
            created_at: datetime = Field(default_factory=datetime.utcnow)

        class UserCreate(UserBase):
            password: str

        class UserRead(UserBase):
            id: int

        return User, UserCreate, UserRead
    except ImportError:
        return None, None, None


def demo_approach_b():
    """Separate Pydantic + SQLAlchemy approach."""
    try:
        from pydantic import BaseModel, Field as PField
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import String

        class Base(DeclarativeBase):
            pass

        class UserORM(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(primary_key=True)
            username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
            email: Mapped[str] = mapped_column(String(255), unique=True)
            full_name: Mapped[str] = mapped_column(String(255), default="")
            password_hash: Mapped[str] = mapped_column(String(255))

        class UserSchema(BaseModel):
            model_config = {"from_attributes": True}
            id: int
            username: str
            email: str
            full_name: str

        return UserORM, UserSchema
    except ImportError:
        return None, None


def demo_trade_offs():
    print("SQLModel Trade-offs: Unified vs Split")
    print()
    print("APPROACH A: SQLModel (Unified)")
    print("  + Single source of truth for schema")
    print("  + Less boilerplate code")
    print("  + Pydantic validation on DB models")
    print("  - Limited static type checking for complex queries")
    print("  - Column comparison issues with mypy/pyright")
    print("  - Less granular control over DB vs API schema")
    print()
    print("APPROACH B: Pydantic + SQLAlchemy (Split)")
    print("  + Full SQLAlchemy 2.0 type checking")
    print("  + Complete control over DB schema")
    print("  + Clear separation of concerns")
    print("  - More code to maintain")
    print("  - Manual mapping between ORM and API models")
    print("  - Risk of schema drift")
    print()
    print("RECOMMENDATION:")
    print("  Simple CRUD apps -> SQLModel (Approach A)")
    print("  Complex queries, relationships -> Split (Approach B)")
    print("  High-performance, type-strict -> Split + Advanced Alchemy")

    demo_approach_a()
    demo_approach_b()


if __name__ == "__main__":
    demo_trade_offs()
