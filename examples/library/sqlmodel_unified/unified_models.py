# requires: sqlmodel sqlalchemy
"""SQLModel unified models: single class for API schema + database table.

Demonstrates:
- SQLModel with table=True
- Field(primary_key=True)
- API model vs table model distinction
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional


def demo_unified_models():
    try:
        from sqlmodel import SQLModel, Field, Session, create_engine, select

        class HeroBase(SQLModel):
            """Shared fields (API schema only, no table)."""
            name: str = Field(index=True)
            secret_name: str
            age: Optional[int] = Field(default=None, index=True)

        class Hero(HeroBase, table=True):
            """Database table model (has an id)."""
            id: Optional[int] = Field(default=None, primary_key=True)
            created_at: datetime = Field(default_factory=datetime.utcnow)

        class HeroCreate(HeroBase):
            """Input model for creating heroes (no id, no timestamps)."""
            pass

        class HeroRead(HeroBase):
            """Output model for reading heroes (includes id)."""
            id: int
            created_at: datetime

        class HeroUpdate(SQLModel):
            """Partial update model."""
            name: Optional[str] = None
            secret_name: Optional[str] = None
            age: Optional[int] = None

        print("SQLModel Unified Models:")
        print(f"  HeroBase (shared fields): {list(HeroBase.model_fields.keys())}")
        print(f"  Hero (table=True): {list(Hero.model_fields.keys())}")
        print(f"  HeroCreate (input): {list(HeroCreate.model_fields.keys())}")
        print(f"  HeroRead (output): {list(HeroRead.model_fields.keys())}")
        print(f"  HeroUpdate (partial): {list(HeroUpdate.model_fields.keys())}")

        db_path = Path(tempfile.gettempdir()) / "sqlmodel_library_unified.sqlite"
        engine = create_engine(f"sqlite:///{db_path}", echo=False)
        SQLModel.metadata.create_all(engine)

        try:
            with Session(engine) as session:
                created = Hero.model_validate(
                    HeroCreate(name="Deadpool", secret_name="Wade Wilson", age=40)
                )
                session.add(created)
                session.commit()
                session.refresh(created)
                print()
                print(f"SQLite CRUD on {db_path}:")
                print(f"  CREATE: id={created.id!r} name={created.name!r} age={created.age}")
                found = session.exec(select(Hero).where(Hero.name == "Deadpool")).first()
                found.age = 41
                session.add(found)
                session.commit()
                session.refresh(found)
                print(f"  UPDATE: id={found.id!r} age={found.age}")
                print(
                    "  READ: "
                    f"{session.exec(select(Hero).where(Hero.id == found.id)).first()!r}"
                )
                session.delete(found)
                session.commit()
                remaining = session.exec(select(Hero)).all()
                print(f"  DELETE: remaining rows={len(remaining)}")
        except Exception as exc:
            print(f"SQLite demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install sqlmodel")


if __name__ == "__main__":
    demo_unified_models()
