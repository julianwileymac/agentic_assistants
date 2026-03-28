# requires: beanie motor pydantic
# optional: mongomock-motor
"""Beanie query patterns: filters, projections, aggregation.

Demonstrates:
- Find with filters and projections
- Sorting, limit, skip
- Aggregation pipelines
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pydantic import BaseModel, Field


def demo_query_patterns():
    print("Beanie Query Patterns (reference):")
    print()
    print("  # Filter with operators")
    print("  results = await Product.find(")
    print("      Product.price >= 10.0,")
    print("      Product.category == 'electronics',")
    print("      Product.in_stock == True,")
    print("  ).to_list()")
    print()
    print("  # Projection (return only specific fields)")
    print("  names = await Product.find_all().project(ProductName).to_list()")
    print()
    print("  # Sorting and pagination")
    print("  page = await Product.find_all()")
    print("      .sort(-Product.price).skip(20).limit(10).to_list()")
    print()
    print("  # Aggregation pipeline")
    print("  results = await Product.aggregate(pipeline).to_list()")
    print()

    try:
        from beanie import Document, Indexed, init_beanie

        class ProductName(BaseModel):
            name: str

        class Product(Document):
            class Settings:
                name = "products_query_demo"

            name: Indexed(str, unique=True)
            description: str = ""
            price: float = Field(gt=0)
            category: Indexed(str)
            tags: list[str] = Field(default_factory=list)
            in_stock: bool = True
            created_at: datetime = Field(default_factory=datetime.utcnow)
            metadata: dict = Field(default_factory=dict)

        async def _run() -> None:
            client = None
            db_name = "beanie_query_patterns_demo"
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
                    print("Skipping executable queries (install mongomock-motor or start MongoDB).")
                    print("  Operations you would run after init_beanie(database=..., document_models=[Product]):")
                    print("    await Product.insert_many([...])  # seed data")
                    print(
                        "    await Product.find(Product.price >= 10, Product.category == 'electronics').to_list()"
                    )
                    print("    await Product.find_all().project(ProductName).to_list()")
                    print("    await Product.find_all().sort(-Product.price).skip(0).limit(2).to_list()")
                    print("    await Product.aggregate([{'$match': ...}, {'$group': ...}]).to_list()")
                    print(f"  (connection error: {conn_exc})")
                    return

            try:
                await init_beanie(
                    database=client[db_name],
                    document_models=[Product],
                )
                await Product.get_motor_collection().delete_many({})
                samples = [
                    Product(
                        name="Phone",
                        price=699.0,
                        category="electronics",
                        in_stock=True,
                        tags=["mobile"],
                    ),
                    Product(
                        name="Book",
                        price=12.0,
                        category="books",
                        in_stock=True,
                        tags=["paper"],
                    ),
                    Product(
                        name="Cable",
                        price=9.99,
                        category="electronics",
                        in_stock=False,
                        tags=["accessory"],
                    ),
                ]
                for p in samples:
                    await p.insert()

                filtered = await Product.find(
                    Product.price >= 10.0,
                    Product.category == "electronics",
                    Product.in_stock == True,  # noqa: E712
                ).to_list()
                print(f"Filtered (price>=10, electronics, in_stock): {[p.name for p in filtered]}")

                projected = await Product.find_all().project(ProductName).to_list()
                print(f"Projection to ProductName: {[m.name for m in projected]}")

                page = (
                    await Product.find_all()
                    .sort(-Product.price)
                    .skip(0)
                    .limit(2)
                    .to_list()
                )
                print(f"Sorted by price desc, limit 2: {[p.name for p in page]}")

                pipeline = [
                    {"$match": {"in_stock": True}},
                    {"$group": {"_id": "$category", "avg_price": {"$avg": "$price"}}},
                    {"$sort": {"avg_price": -1}},
                ]
                agg = await Product.aggregate(pipeline).to_list()
                print(f"Aggregation avg price by category: {agg}")
            finally:
                if client is not None:
                    client.close()

        try:
            asyncio.run(_run())
        except Exception as exc:
            print(f"Query demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install beanie motor")


if __name__ == "__main__":
    demo_query_patterns()
