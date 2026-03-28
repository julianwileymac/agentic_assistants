# requires: advanced-alchemy sqlalchemy aiosqlite
"""Advanced Alchemy service layer with lifecycle hooks.

Demonstrates:
- SQLAlchemyAsyncRepositoryService
- before_create / after_update hooks
- Bulk operations
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


def demo_service_layer():
    """Show the Advanced Alchemy service pattern."""
    try:
        from advanced_alchemy.base import UUIDAuditBase
        from advanced_alchemy.repository import SQLAlchemyAsyncRepository
        from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

        class Product(UUIDAuditBase):
            __tablename__ = "products"
            name: Mapped[str] = mapped_column(String(255))
            sku: Mapped[str] = mapped_column(String(50), unique=True)
            price: Mapped[float] = mapped_column(default=0.0)
            description: Mapped[Optional[str]] = mapped_column(Text, default=None)

        class ProductRepository(SQLAlchemyAsyncRepository[Product]):
            model_type = Product

        class ProductService(SQLAlchemyAsyncRepositoryService[Product]):
            """Service with business logic hooks."""

            repository_type = ProductRepository

            async def to_model_on_create(self, data: Any) -> Any:
                sku = data.get("sku") if isinstance(data, dict) else getattr(data, "sku", None)
                print("  [hook] to_model_on_create:", sku)
                return await super().to_model_on_create(data)

            async def to_model_on_update(self, data: Any) -> Any:
                sku = data.get("sku") if isinstance(data, dict) else getattr(data, "sku", None)
                print("  [hook] to_model_on_update:", sku)
                return await super().to_model_on_update(data)

        print("Advanced Alchemy Service Layer:")
        print("  ProductService wraps ProductRepository with lifecycle hooks.")
        print()
        print("  Built-in customization points (async) include:")
        print("    - to_model_on_create / to_model_on_update / to_model_on_delete / to_model_on_upsert")
        print("    - Override these to adjust data before persistence (see ProductService below).")
        print()
        print("  Bulk operations:")
        print("    - create_many(data_list)")
        print("    - update_many(data_list)")

        print("\n--- Async SQLite: service create / update / list ---")
        try:
            import asyncio

            from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

            async def _service_demo() -> None:
                engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
                async with engine.begin() as conn:
                    await conn.run_sync(Product.metadata.create_all)

                session_factory = async_sessionmaker(engine, expire_on_commit=False)
                async with session_factory() as session:
                    service = ProductService(session=session)
                    p = await service.create(
                        {"name": "Sensor Kit", "sku": "SKU-100", "price": 49.99, "description": None},
                        auto_commit=True,
                    )
                    print(f"  created: {p.sku} price={p.price}")

                    p.price = 39.99
                    updated = await service.update(p, auto_commit=True)
                    print(f"  updated price: {updated.price}")

                    rows = await service.list()
                    print(f"  list count: {len(rows)}")

            asyncio.run(_service_demo())
        except ImportError as e:
            print(f"  Skipping service demo: {e}")
        except Exception as e:
            print(f"  Service demo failed ({type(e).__name__}: {e})")

    except ImportError:
        print("Install: pip install advanced-alchemy sqlalchemy aiosqlite")


def main() -> None:
    """Run the service layer + hooks example."""
    demo_service_layer()


if __name__ == "__main__":
    main()
