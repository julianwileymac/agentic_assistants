# requires: advanced-alchemy litestar sqlalchemy aiosqlite
"""Advanced Alchemy + Litestar DTO integration.

Demonstrates:
- SQLAlchemyDTO for automatic model-to-API conversion
- DTOConfig to exclude internal fields
- Read vs Write DTOs
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


def demo_dto_integration():
    """Show Advanced Alchemy models with Litestar DTO boundaries."""
    try:
        from advanced_alchemy.base import UUIDAuditBase, model_to_dict
        from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
        from litestar.dto import DTOConfig

        class User(UUIDAuditBase):
            __tablename__ = "users"
            username: Mapped[str] = mapped_column(String(100))
            email: Mapped[str] = mapped_column(String(255))
            password_hash: Mapped[str] = mapped_column(String(255))
            bio: Mapped[Optional[str]] = mapped_column(Text, default=None)

        class UserReadDTO(SQLAlchemyDTO[User]):
            config = DTOConfig(
                exclude={"password_hash", "sa_orm_sentinel"},
                rename_strategy="camel",
            )

        class UserCreateDTO(SQLAlchemyDTO[User]):
            config = DTOConfig(
                exclude={"id", "created_at", "updated_at", "sa_orm_sentinel"},
                rename_strategy="camel",
            )

        class UserUpdateDTO(SQLAlchemyDTO[User]):
            config = DTOConfig(
                exclude={
                    "id",
                    "username",
                    "email",
                    "password_hash",
                    "created_at",
                    "updated_at",
                    "sa_orm_sentinel",
                },
                rename_strategy="camel",
            )

        print("Advanced Alchemy + Litestar DTO Integration:")
        print(f"  User model columns: {[c.name for c in User.__table__.columns]}")
        print()
        print("  UserReadDTO excludes: password_hash")
        print("  UserCreateDTO excludes: id, created_at, updated_at")
        print("  UserUpdateDTO allows patching: bio (identity + secrets excluded)")
        print("  All use camelCase renaming for JSON keys")

        print("\n--- DTO-shaped boundary flow (async SQLite) ---")
        try:
            import asyncio
            from datetime import datetime
            from uuid import UUID

            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            def _camel_case(snake: str) -> str:
                parts = snake.split("_")
                return parts[0] + "".join(p.title() for p in parts[1:])

            def _read_dto_dict(user: User) -> dict[str, object]:
                raw = model_to_dict(user, exclude={"password_hash"})
                out: dict[str, object] = {}
                for key, value in raw.items():
                    if isinstance(value, UUID):
                        out[_camel_case(key)] = str(value)
                    elif isinstance(value, datetime):
                        out[_camel_case(key)] = value.isoformat()
                    else:
                        out[_camel_case(key)] = value
                return out

            async def _dto_flow() -> None:
                engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
                async with engine.begin() as conn:
                    await conn.run_sync(User.metadata.create_all)

                session_factory = async_sessionmaker(engine, expire_on_commit=False)

                # Client JSON as UserCreateDTO would receive (camelCase)
                create_body = {
                    "username": "dana",
                    "email": "dana@example.com",
                    "passwordHash": "hashed-demo-secret",
                    "bio": "Platform engineer",
                }
                user = User(
                    username=create_body["username"],
                    email=create_body["email"],
                    password_hash=create_body["passwordHash"],
                    bio=create_body["bio"],
                )
                async with session_factory() as session:
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)

                    print("  CreateDTO-shaped payload applied -> ORM row id =", user.id)
                    print("  ReadDTO-shaped response:", _read_dto_dict(user))

                    patch = {"bio": "Staff engineer (updated)"}  # UpdateDTO-shaped: only allowed fields
                    user.bio = patch["bio"]
                    await session.commit()
                    await session.refresh(user)

                    print("  After UpdateDTO-shaped patch:", _read_dto_dict(user))

            asyncio.run(_dto_flow())
        except ImportError as e:
            print(f"  Skipping DTO flow demo: {e}")
        except Exception as e:
            print(f"  DTO flow demo failed ({type(e).__name__}: {e})")

    except ImportError:
        print("Install: pip install advanced-alchemy litestar sqlalchemy aiosqlite")


def main() -> None:
    """Run the Litestar DTO + SQLAlchemy boundary example."""
    demo_dto_integration()


if __name__ == "__main__":
    main()
