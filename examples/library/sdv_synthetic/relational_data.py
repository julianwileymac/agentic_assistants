# requires: sdv, pandas

"""Multi-table synthetic data: parent customers + child orders with HMASynthesizer."""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from sdv.metadata import Metadata
        from sdv.multi_table import HMASynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv and pandas to run this example:", exc)
        return

    rng = np.random.default_rng(7)
    n_customers = 40
    customer_ids = np.arange(1, n_customers + 1)

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "name": [f"Customer {i}" for i in customer_ids],
            "country": rng.choice(["US", "CA", "UK", "DE", "JP"], size=n_customers),
            "signup_year": rng.integers(2018, 2025, size=n_customers),
        }
    )

    n_orders = 220
    orders = pd.DataFrame(
        {
            "order_id": np.arange(1, n_orders + 1),
            "customer_id": rng.choice(customer_ids, size=n_orders),
            "amount": np.round(rng.uniform(15.0, 450.0, size=n_orders), 2),
            "status": rng.choice(["pending", "shipped", "delivered", "returned"], size=n_orders, p=[0.1, 0.2, 0.65, 0.05]),
        }
    )

    print("Real data - customers head:")
    print(customers.head().to_string(index=False))
    print("\nReal data - orders head:")
    print(orders.head().to_string(index=False))

    metadata = Metadata.detect_from_dataframes(
        {"customers": customers, "orders": orders},
    )

    print("\nMulti-table metadata (tables and relationships):")
    print(metadata)

    synthesizer = HMASynthesizer(metadata, verbose=False)
    print("\nFitting HMASynthesizer on relational data...")
    synthesizer.fit({"customers": customers, "orders": orders})

    print("\nSampling synthetic database...")
    synthetic = synthesizer.sample(scale=1.0)

    print("\n" + "=" * 60)
    print("SYNTHETIC TABLES")
    print("=" * 60)
    synth_customers = synthetic["customers"]
    synth_orders = synthetic["orders"]

    print(f"\nSynthetic customers ({len(synth_customers)} rows):")
    print(synth_customers.to_string(index=False))

    print(f"\nSynthetic orders ({len(synth_orders)} rows):")
    print(synth_orders.to_string(index=False))

    # Referential sanity: every order.customer_id should exist in synthetic customers.
    valid_fk = synth_orders["customer_id"].isin(synth_customers["customer_id"]).mean()
    print(f"\nShare of orders whose customer_id exists in synthetic customers: {valid_fk:.2%}")


if __name__ == "__main__":
    main()
