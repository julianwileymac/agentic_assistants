# requires: faker, pandas

"""Bulk tabular data with Faker: reproducible customer DataFrame for ML-style demos."""

from __future__ import annotations


def main() -> None:
    try:
        import pandas as pd
        from faker import Faker
    except ImportError as exc:  # pragma: no cover
        print("Install faker and pandas to run this example:", exc)
        return

    fake = Faker()
    fake.seed_instance(20250327)

    n = 1000
    rows = []
    for _ in range(n):
        rows.append(
            {
                "name": fake.name(),
                "email": fake.email(),
                "age": fake.random_int(min=18, max=79),
                "salary": round(fake.random_int(min=35_000, max=185_000) + fake.pyfloat(min_value=0, max_value=0.99), 2),
                "signup_date": fake.date_between(start_date="-10y", end_date="today"),
                "country": fake.country_code(representation="alpha-2"),
            }
        )

    df = pd.DataFrame(rows)

    print(f"Generated customers DataFrame: {len(df)} rows")
    print("\nDataFrame.info():")
    df.info()
    print("\nHead:")
    print(df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
