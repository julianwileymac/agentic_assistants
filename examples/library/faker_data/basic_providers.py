# requires: faker

"""Faker basics: core providers, multiple locales, and a tiny custom provider."""

from __future__ import annotations

import sys


def main() -> None:
    try:
        from faker import Faker
        from faker.providers import BaseProvider
    except ImportError as exc:  # pragma: no cover
        print("Install faker to run this example:", exc)
        return

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

    class ProductSKUProvider(BaseProvider):
        """Minimal custom provider: synthetic SKU-style codes."""

        def sku(self, prefix: str = "SKU") -> str:
            suffix = self.bothify(text="??-###", letters="ABCDEFGHJKLMNPQRSTUVWXYZ")
            return f"{prefix}-{suffix}"

    records = []

    for locale in ("en_US", "fr_FR", "ja_JP"):
        fake = Faker(locale)
        fake.seed_instance(42)
        fake.add_provider(ProductSKUProvider)
        records.append(
            {
                "locale": locale,
                "name": fake.name(),
                "address": fake.address().replace("\n", ", "),
                "birthdate": fake.date_of_birth(minimum_age=22, maximum_age=70).isoformat(),
                "email": fake.email(),
                "company_bs": fake.bs(),
                "sku": fake.sku("ITEM"),
            }
        )

    # Remaining rows use default locale with varied providers
    fake_us = Faker("en_US")
    fake_us.seed_instance(99)
    fake_us.add_provider(ProductSKUProvider)
    for _ in range(7):
        records.append(
            {
                "locale": "en_US",
                "name": fake_us.name(),
                "address": fake_us.street_address() + ", " + fake_us.city() + ", " + fake_us.state_abbr(),
                "birthdate": fake_us.date_this_decade().isoformat(),
                "email": fake_us.company_email(),
                "company_bs": fake_us.catch_phrase(),
                "sku": fake_us.sku("CAT"),
            }
        )

    print("10 sample records (names, addresses, dates, emails, text, custom SKU):")
    print("-" * 72)
    for i, row in enumerate(records, start=1):
        print(f"{i:2}. [{row['locale']}] {row['name']} <{row['email']}>")
        print(f"     addr: {row['address']}")
        print(f"     date: {row['birthdate']} | text: {row['company_bs']}")
        print(f"     sku:  {row['sku']}")
        print()


if __name__ == "__main__":
    main()
