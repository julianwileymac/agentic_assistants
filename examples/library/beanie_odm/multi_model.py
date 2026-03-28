# requires: beanie motor pydantic
# optional: mongomock-motor
"""Beanie multi-model pattern: different models for different lifecycle stages.

Demonstrates:
- CreateProduct (input), Product (DB), ProductResponse (output)
- Separation of concerns at API boundaries
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    """Input model for creating a product (no id, no timestamps)."""
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    category: str
    description: str = ""


class ProductResponse(BaseModel):
    """Output model for API responses (excludes internal fields)."""
    id: str
    name: str
    price: float
    category: str
    description: str
    created_at: datetime


def demo_multi_model():
    try:
        from beanie import Document, Indexed

        class Product(Document):
            """Full database document with all fields."""
            class Settings:
                name = "products"

            name: Indexed(str, unique=True)
            price: float
            category: Indexed(str)
            description: str = ""
            internal_sku: str = ""
            cost_price: float = 0.0
            created_at: datetime = Field(default_factory=datetime.utcnow)

        print("Multi-model lifecycle pattern:")
        print(f"  CreateProduct fields: {list(CreateProduct.model_fields.keys())}")
        print(f"  Product (DB) fields:  {list(Product.model_fields.keys())}")
        print(f"  ProductResponse fields: {list(ProductResponse.model_fields.keys())}")
        print()
        print("  Flow: CreateProduct -> Product.insert() -> ProductResponse")
        print("  Internal fields (internal_sku, cost_price) never leak to API")

        async def _run() -> None:
            from beanie import init_beanie

            client = None
            db_name = "beanie_multi_model_demo"
            try:
                from mongomock_motor import AsyncMongoMockClient

                client = AsyncMongoMockClient()
            except ImportError:
                try:
                    from motor.motor_asyncio import AsyncIOMotorClient

                    client = AsyncIOMotorClient(
                        "mongodb://localhost:27017",
                        serverSelectionTimeoutMS=2500,
                    )
                    await client.admin.command("ping")
                except Exception as conn_exc:
                    print()
                    print("Skipping live multi-model demo (mongomock-motor or MongoDB required).")
                    print("  Would: payload = CreateProduct(...); doc = Product(...); await doc.insert()")
                    print(f"  ({conn_exc})")
                    return

            try:
                await init_beanie(
                    database=client[db_name],
                    document_models=[Product],
                )
                await Product.get_motor_collection().delete_many({})
                payload = CreateProduct(
                    name="API Widget",
                    price=42.0,
                    category="demo",
                    description="From CreateProduct DTO",
                )
                doc = Product(
                    **payload.model_dump(),
                    internal_sku="SKU-SECRET",
                    cost_price=10.0,
                )
                await doc.insert()
                api_out = ProductResponse(
                    id=str(doc.id),
                    name=doc.name,
                    price=doc.price,
                    category=doc.category,
                    description=doc.description,
                    created_at=doc.created_at,
                )
                print()
                print("Live path: CreateProduct -> Product (with internal fields) -> ProductResponse")
                print(f"  Response (no internal_sku): {api_out.model_dump()}")
            finally:
                if client is not None:
                    client.close()

        try:
            asyncio.run(_run())
        except Exception as exc:
            print(f"Multi-model demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install beanie motor")


if __name__ == "__main__":
    demo_multi_model()
