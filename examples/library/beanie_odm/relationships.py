# requires: beanie motor pydantic
# optional: mongomock-motor
"""Beanie document relationships with Link[T].

Demonstrates:
- Link references between documents
- Fetching linked documents
- Back-populate pattern
"""

from __future__ import annotations

import asyncio


def demo_relationships():
    try:
        from beanie import Document, Link, Indexed

        class Author(Document):
            class Settings:
                name = "authors"
            name: str
            email: Indexed(str, unique=True)

        class Book(Document):
            class Settings:
                name = "books"
            title: str
            author: Link[Author]
            isbn: Indexed(str, unique=True)

        print("Beanie Relationships with Link[T]:")
        print()
        print("  # Create linked documents")
        print("  author = Author(name='Jane', email='jane@example.com')")
        print("  await author.insert()")
        print()
        print("  book = Book(title='Python Mastery', author=author, isbn='123')")
        print("  await book.insert()")
        print()
        print("  # Fetch with links resolved")
        print("  book = await Book.find_one(Book.isbn == '123', fetch_links=True)")
        print("  print(book.author.name)  # 'Jane'")
        print()
        print("  # Without fetch_links, author is a DBRef (lazy)")
        print("  book = await Book.find_one(Book.isbn == '123')")
        print("  # book.author is a Link reference, not the full Author")

        async def _run() -> None:
            from beanie import init_beanie

            client = None
            db_name = "beanie_relationships_demo"
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
                    print("Skipping live Link demo (mongomock-motor or MongoDB required).")
                    print("  After await init_beanie(database=..., document_models=[Author, Book]):")
                    print("    author = Author(name='Jane', email='jane@example.com'); await author.insert()")
                    print(
                        "    book = Book(title='Python Mastery', author=author, isbn='123'); await book.insert()"
                    )
                    print(
                        "    loaded = await Book.find_one(Book.isbn == '123', fetch_links=True)  # resolves Link"
                    )
                    print(f"  (connection error: {conn_exc})")
                    return

            try:
                await init_beanie(
                    database=client[db_name],
                    document_models=[Author, Book],
                )
                await Author.get_motor_collection().delete_many({})
                await Book.get_motor_collection().delete_many({})
                author = Author(name="Jane", email="jane@example.com")
                await author.insert()
                book = Book(title="Python Mastery", author=author, isbn="123")
                await book.insert()
                with_link = await Book.find_one(Book.isbn == "123", fetch_links=True)
                if with_link is not None:
                    print()
                    print(
                        "Live demo: fetch_links=True -> author name:",
                        getattr(with_link.author, "name", with_link.author),
                    )
            finally:
                if client is not None:
                    client.close()

        try:
            asyncio.run(_run())
        except Exception as exc:
            print(f"Relationship demo error: {type(exc).__name__}: {exc}")

    except ImportError:
        print("Install: pip install beanie motor")


if __name__ == "__main__":
    demo_relationships()
