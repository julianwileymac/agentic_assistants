# requires: faker, pandas

"""Domain-shaped factories: finance, healthcare-style, and e-commerce order tables."""

from __future__ import annotations

_pd = None
_Faker = None


def _deps():
    """Load third-party deps once; raises ImportError with context if missing."""
    global _pd, _Faker
    if _pd is not None and _Faker is not None:
        return _pd, _Faker
    try:
        import pandas as pd
        from faker import Faker
    except ImportError as exc:
        raise ImportError("Install faker and pandas.") from exc
    _pd, _Faker = pd, Faker
    return pd, Faker


def make_financial_transactions_df(n: int = 120):
    try:
        pd, Faker = _deps()
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install faker and pandas to use make_financial_transactions_df") from exc

    fake = Faker()
    fake.seed_instance(11)
    rows = []
    for _ in range(n):
        rows.append(
            {
                "amount": round(fake.pyfloat(min_value=4.5, max_value=2_500.0, right_digits=2), 2),
                "merchant": fake.company(),
                "card_type": fake.random_element(elements=("visa", "mastercard", "amex", "discover")),
                "timestamp": fake.date_time_between(start_date="-90d", end_date="now"),
            }
        )
    return pd.DataFrame(rows)


def make_medical_records_df(n: int = 80):
    try:
        pd, Faker = _deps()
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install faker and pandas to use make_medical_records_df") from exc

    fake = Faker()
    fake.seed_instance(73)
    diagnoses = ("Hypertension", "Type II Diabetes", "Asthma", "Migraine", "GERD", "Anxiety disorder")
    procedures = ("EKG", "Lipid panel", "Spirometry", "CT head", "Colonoscopy", "Physical therapy session")
    rows = []
    for _ in range(n):
        rows.append(
            {
                "patient_id": fake.uuid4(),
                "diagnosis": fake.random_element(elements=diagnoses),
                "procedure": fake.random_element(elements=procedures),
                "cost": round(fake.pyfloat(min_value=120.0, max_value=9_500.0, right_digits=2), 2),
            }
        )
    return pd.DataFrame(rows)


def make_ecommerce_orders_df(n: int = 100):
    try:
        pd, Faker = _deps()
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install faker and pandas to use make_ecommerce_orders_df") from exc

    fake = Faker()
    fake.seed_instance(404)
    products = ("Noise-canceling headphones", "Stainless bottle", "USB-C hub", "Desk lamp", "Yoga mat")
    statuses = ("pending", "paid", "shipped", "delivered", "returned")
    rows = []
    for _ in range(n):
        qty = fake.random_int(min=1, max=5)
        unit = round(fake.pyfloat(min_value=9.99, max_value=249.99, right_digits=2), 2)
        rows.append(
            {
                "product": fake.random_element(elements=products),
                "quantity": qty,
                "price": unit,
                "status": fake.random_element(elements=statuses),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    try:
        _deps()
    except ImportError as exc:  # pragma: no cover
        print("Install faker and pandas to run this example:", exc)
        return

    fin = make_financial_transactions_df(8)
    med = make_medical_records_df(6)
    shop = make_ecommerce_orders_df(7)

    print("Financial transactions (sample):")
    print(fin.to_string(index=False))
    print("\nMedical-style records (sample):")
    print(med.to_string(index=False))
    print("\nE-commerce orders (sample):")
    print(shop.to_string(index=False))


if __name__ == "__main__":
    main()
