# requires: sdv

"""Privacy-oriented metrics on synthetic tabular data (k-anonymity-style + SDMetrics)."""

from __future__ import annotations


def _k_anonymity_min_group(df, quasi_identifiers: list[str]) -> tuple[int, float]:
    """Return minimum group size and fraction of rows in groups with k>=5 (toy k-anonymity view)."""
    counts = df.groupby(quasi_identifiers, dropna=False).size()
    k_min = int(counts.min()) if len(counts) else 0
    ge5 = counts[counts >= 5].sum()
    frac = float(ge5 / len(df)) if len(df) else 0.0
    return k_min, frac


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from sdmetrics.single_table.privacy import DisclosureProtection, NumericalMLP
        from sdv.evaluation.single_table import evaluate_quality
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv, sdmetrics, pandas, numpy, scikit-learn to run this example:", exc)
        return

    print("Privacy vs quality: k-anonymity-style groups, DisclosureProtection, NumericalMLP attacker")
    print("-" * 60)

    rng = np.random.default_rng(7)
    n = 200
    region = rng.choice(["NE", "SW", "MW"], size=n)
    age_bucket = rng.integers(25, 66, size=n) // 10
    income_k = rng.integers(40, 160, size=n)
    sensitive_score = (age_bucket * 3 + rng.normal(0, 2, size=n)).round(2)

    real_data = pd.DataFrame(
        {
            "region": region,
            "age_bucket": age_bucket,
            "income_k": income_k,
            "risk_score": sensitive_score,
        }
    )

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)

    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(real_data)
    synthetic_data = synthesizer.sample(num_rows=n)

    quasi = ["region", "age_bucket"]
    k_min_real, frac5_real = _k_anonymity_min_group(real_data, quasi)
    k_min_syn, frac5_syn = _k_anonymity_min_group(synthetic_data, quasi)
    print("K-anonymity-style (quasi-identifiers region + age_bucket):")
    print(f"  real:       min group size={k_min_real}, fraction in groups k>=5: {frac5_real:.3f}")
    print(f"  synthetic:  min group size={k_min_syn}, fraction in groups k>=5: {frac5_syn:.3f}")

    # Disclosure / membership-style risk: attacker learns sensitive columns from quasi-identifiers
    # trained on synthetic data, evaluated on held-out real rows (SDMetrics pattern).
    disc = DisclosureProtection.compute(
        real_data,
        synthetic_data,
        known_column_names=["region", "age_bucket", "income_k"],
        sensitive_column_names=["risk_score"],
        computation_method="cap",
        continuous_column_names=["income_k", "risk_score"],
        num_discrete_bins=8,
    )
    print("\nDisclosureProtection score (higher => safer vs naive CAP attacker):", f"{disc:.4f}")

    # NumericalMLP accepts numeric / object dtypes per sdmetrics; exclude raw categorical keys.
    mlp_score = NumericalMLP.compute(
        real_data,
        synthetic_data,
        key_fields=["age_bucket", "income_k"],
        sensitive_fields=["risk_score"],
    )
    print(
        "NumericalMLP privacy metric (numeric quasi-keys age_bucket + income_k -> risk_score; "
        "higher is better per sdmetrics Goal.MAXIMIZE):",
        mlp_score,
    )

    print("\nQuality report (SDV evaluate_quality / SDMetrics - higher is better fidelity):")
    report = evaluate_quality(
        real_data=real_data,
        synthetic_data=synthetic_data,
        metadata=metadata,
        verbose=False,
    )
    q_score = report.get_score()
    print(f"  overall quality: {q_score:.4f}")
    print(
        "\nTrade-off narrative: stronger privacy often correlates with lower fidelity; "
        "compare DisclosureProtection / attacker metrics with the quality headline score."
    )


if __name__ == "__main__":
    main()
