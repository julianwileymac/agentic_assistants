# requires: sdv, pandas

"""CTGAN single-table synthesis: complex mixed types, epochs=100, distribution comparison."""

from __future__ import annotations


def main() -> None:
    try:
        import ctgan  # noqa: F401 — SDV's CTGANSynthesizer wraps this package
        import numpy as np
        import pandas as pd
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import CTGANSynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv, pandas, and ctgan to run this example:", exc)
        return

    rng = np.random.default_rng(42)
    n = 800
    categories = np.array(["groceries", "gas", "online", "travel", "cash_advance", "utilities"])
    cat_idx = rng.integers(0, len(categories), size=n)
    base_time = np.datetime64("2024-01-01")
    timestamps = base_time + rng.integers(0, 180, size=n).astype("timedelta64[D]")

    # Fraud is rarer and skewed toward certain categories (synthetic but structured).
    fraud_prob = np.where(np.isin(cat_idx, [2, 4]), 0.12, 0.02)
    is_fraud = rng.random(n) < fraud_prob
    amount = rng.lognormal(mean=3.5, sigma=1.1, size=n) * (1.0 + 0.35 * is_fraud)

    transactions = pd.DataFrame(
        {
            "amount": amount.round(2),
            "category": categories[cat_idx],
            "timestamp": pd.to_datetime(timestamps.astype(str)),
            "is_fraud": is_fraud.astype(bool),
        }
    )

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(transactions)

    print("Transaction schema (detected):")
    for col, meta in metadata.columns.items():
        print(f"  {col}: {meta.get('sdtype')}")

    print("\nFitting CTGANSynthesizer (epochs=100; may take a minute)...")
    synthesizer = CTGANSynthesizer(metadata, epochs=100, verbose=False)
    synthesizer.fit(transactions)

    synthetic = synthesizer.sample(num_rows=600)

    print("\n" + "=" * 60)
    print("Distribution comparison - original vs synthetic")
    print("=" * 60)

    print("\nAmount - describe():")
    print("  original:\n", transactions["amount"].describe().to_string())
    print("  synthetic:\n", synthetic["amount"].describe().to_string())

    print("\nCategory - value counts (normalized):")
    o_cat = transactions["category"].value_counts(normalize=True).sort_index()
    s_cat = synthetic["category"].value_counts(normalize=True).sort_index()
    compare_cat = pd.DataFrame({"orig": o_cat, "synth": s_cat}).fillna(0)
    print(compare_cat.to_string())

    print("\nis_fraud - rate:")
    print(f"  original fraud rate:   {transactions['is_fraud'].mean():.4f}")
    print(f"  synthetic fraud rate:  {synthetic['is_fraud'].mean():.4f}")

    print("\nTimestamp - monthly counts (first 6 months shown):")
    o_m = transactions["timestamp"].dt.to_period("M").value_counts().sort_index().head(6)
    s_m = synthetic["timestamp"].dt.to_period("M").value_counts().sort_index().head(6)
    print("  original:\n", o_m.to_string())
    print("  synthetic:\n", s_m.to_string())

    print("\nSample synthetic rows:")
    print(synthetic.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
