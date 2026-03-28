# requires: beanie motor pydantic
# optional: mongomock-motor (in-memory MongoDB for local runs without a server)
"""Beanie Document models for MongoDB.

Demonstrates:
- Document class with indexes
- Settings inner class
- Embedded documents
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from pydantic import Field


def demo_document_models():
    try:
        from beanie import Document, Indexed

        class Address(Document):
            """Embedded address (also a Document for standalone use)."""

            class Settings:
                name = "addresses"

            street: str
            city: str
            state: str = ""
            country: str = "US"
            zip_code: str = ""

        class Product(Document):
            """Product with indexes and validation."""

            class Settings:
                name = "products"
                indexes = [
                    "category",
                    [("name", 1), ("category", 1)],
                ]

            name: Indexed(str, unique=True)
            description: str = ""
            price: float = Field(gt=0)
            category: Indexed(str)
            tags: list[str] = Field(default_factory=list)
            in_stock: bool = True
            created_at: datetime = Field(default_factory=datetime.utcnow)
            metadata: dict = Field(default_factory=dict)

        class User(Document):
            class Settings:
                name = "users"

            username: Indexed(str, unique=True)
            email: Indexed(str, unique=True)
            full_name: str = ""
            address: Optional[Address] = None
            is_active: bool = True

        print("Beanie Document Models:")
        for cls in [Product, User, Address]:
            print(f"  {cls.__name__} -> collection: {cls.Settings.name}")
            print(f"    Fields: {list(cls.model_fields.keys())}")

        print()
        print("init_beanie (production) attaches models to a Motor database, e.g.:")
        print("  await init_beanie(database=client.mydb, document_models=[Product, User, Address])")

        async def _run_live() -> None:
            from beanie import init_beanie

            client = None
            db_name = "beanie_docmodels_demo"
            try:
                from mongomock_motor import AsyncMongoMockClient

                client = AsyncMongoMockClient()
                print("Using mongomock-motor (pip install mongomock-motor) — no real MongoDB needed.")
            except ImportError:
                try:
                    from motor.motor_asyncio import AsyncIOMotorClient

                    client = AsyncIOMotorClient(
                        "mongodb://localhost:27017",
                        serverSelectionTimeoutMS=2500,
                    )
                    await client.admin.command("ping")
                    print("Connected to local MongoDB at mongodb://localhost:27017")
                except Exception as conn_exc:
                    print("No in-memory mock and no reachable MongoDB.")
                    print("  Install: pip install mongomock-motor")
                    print("  Or start MongoDB, then re-run.")
                    print(f"  (connection check failed: {conn_exc})")
                    print()
                    print("Operations you would run after init_beanie:")
                    print("  p = Product(name='Demo', price=9.99, category='demo', tags=['a'])")
                    print("  await p.insert()")
                    print("  found = await Product.find_one(Product.name == 'Demo')")
                    return

            try:
                await init_beanie(
                    database=client[db_name],
                    document_models=[Product, User, Address],
                )
                demo_product = Product(
                    name="demo-product",
                    price=19.99,
                    category="samples",
                    tags=["doc", "model"],
                )
                await demo_product.insert()
                loaded = await Product.find_one(Product.name == "demo-product")
                print(f"Live CRUD smoke test: inserted and loaded id={getattr(loaded, 'id', None)!r}")
            finally:
                if client is not None:
                    client.close()

        try:
            asyncio.run(_run_live())
        except Exception as exc:
            print(f"Async demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install beanie motor")


if __name__ == "__main__":
    demo_document_models()
