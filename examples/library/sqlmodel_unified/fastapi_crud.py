# requires: sqlmodel fastapi uvicorn
"""SQLModel + FastAPI full CRUD API.

Demonstrates:
- Session dependency injection
- Create, Read, Update, Delete endpoints
- SQLModel as request/response models
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

try:
    from sqlmodel import SQLModel, Field, Session, create_engine, select
    from fastapi import FastAPI, Depends, HTTPException

    _db_path = Path(tempfile.gettempdir()) / "sqlmodel_library_fastapi_crud.sqlite"
    engine = create_engine(f"sqlite:///{_db_path}", echo=False)

    class Item(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True)
        price: float
        description: str = ""

    class ItemCreate(SQLModel):
        name: str
        price: float
        description: str = ""

    class ItemUpdate(SQLModel):
        name: Optional[str] = None
        price: Optional[float] = None
        description: Optional[str] = None

    SQLModel.metadata.create_all(engine)

    app = FastAPI(title="Items API")

    def get_session():
        with Session(engine) as session:
            yield session

    @app.post("/items", response_model=Item)
    def create_item(item: ItemCreate, session: Session = Depends(get_session)):
        db_item = Item.model_validate(item)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @app.get("/items", response_model=list[Item])
    def read_items(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
        return session.exec(select(Item).offset(skip).limit(limit)).all()

    @app.get("/items/{item_id}", response_model=Item)
    def read_item(item_id: int, session: Session = Depends(get_session)):
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @app.patch("/items/{item_id}", response_model=Item)
    def update_item(item_id: int, item: ItemUpdate, session: Session = Depends(get_session)):
        db_item = session.get(Item, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item

    @app.delete("/items/{item_id}")
    def delete_item(item_id: int, session: Session = Depends(get_session)):
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        session.delete(item)
        session.commit()
        return {"ok": True}

    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False
    engine = None

    from fastapi import FastAPI

    app = FastAPI(title="Items API (install dependencies)")

    @app.get("/")
    def root():
        return {
            "detail": "Install: pip install sqlmodel fastapi uvicorn",
            "hint": "Module-level app exists so uvicorn can load this module.",
        }


def demo_fastapi_crud():
    print("SQLModel + FastAPI CRUD API:")
    print("  POST   /items         - Create item")
    print("  GET    /items         - List items")
    print("  GET    /items/{id}    - Get item")
    print("  PATCH  /items/{id}    - Update item")
    print("  DELETE /items/{id}    - Delete item")
    print()
    print("  Run: uvicorn examples.library.sqlmodel_unified.fastapi_crud:app --reload")
    print()

    if not _DEPS_OK or engine is None:
        print("Install: pip install sqlmodel fastapi uvicorn")
        try:
            from fastapi.testclient import TestClient

            with TestClient(app) as client:
                r = client.get("/")
                print(f"Stub app GET / -> {r.status_code} {r.json()}")
        except Exception as exc:
            print(f"TestClient stub error: {type(exc).__name__}: {exc}")
        return

    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as client:
            r = client.post(
                "/items",
                json={"name": "Demo", "price": 3.5, "description": "from TestClient"},
            )
            print(f"POST /items -> {r.status_code} {r.json()}")
            item_id = r.json()["id"]
            r2 = client.get(f"/items/{item_id}")
            print(f"GET /items/{item_id} -> {r2.json()}")
            r3 = client.patch(f"/items/{item_id}", json={"price": 4.0})
            print(f"PATCH /items/{item_id} -> {r3.json()}")
            r4 = client.delete(f"/items/{item_id}")
            print(f"DELETE /items/{item_id} -> {r4.json()}")
    except Exception as exc:
        print(f"TestClient demo error: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    demo_fastapi_crud()
