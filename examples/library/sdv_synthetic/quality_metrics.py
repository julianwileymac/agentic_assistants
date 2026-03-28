# requires: sdv, sdmetrics, pandas

"""SDMetrics via SDV evaluate_quality: column shapes & column pair trends (quality report)."""

from __future__ import annotations

import random
import sys


def main() -> None:
    try:
        import pandas as pd
        import sdmetrics
        from sdv.evaluation.single_table import evaluate_quality
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv, sdmetrics, and pandas to run this example:", exc)
        return

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

    print(f"SDMetrics version: {sdmetrics.__version__}")

    # Enough rows for a stable Gaussian-copula fit (tiny tables can produce wild numerics).
    random.seed(42)
    rows = []
    for _ in range(160):
        hours = random.randint(2, 10)
        prior = int(max(45, min(95, random.gauss(52 + hours * 2.8, 7.0))))
        passed = (prior >= 72 and hours >= 5) or (prior >= 80)
        if random.random() < 0.12:
            passed = not passed
        track = random.choice(["A", "B"])
        rows.append(
            {
                "hours_studied": hours,
                "prior_score": prior,
                "passed": passed,
                "track": track,
            }
        )
    real_data = pd.DataFrame(rows)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(real_data)

    synthesizer = GaussianCopulaSynthesizer(metadata)
    synthesizer.fit(real_data)
    synthetic_data = synthesizer.sample(num_rows=len(real_data))

    print("\nReal vs synthetic (first rows):")
    print("Real:\n", real_data.head().to_string(index=False))
    print("Synthetic:\n", synthetic_data.head().to_string(index=False))

    # evaluate_quality() drives SDMetrics' QualityReport, whose two headline properties are
    # "Column Shapes" and "Column Pair Trends" (the practical successors to the older
    # ColumnShapeScore / ColumnPairTrendsScore naming in docs and tutorials).
    print("\nRunning evaluate_quality() (SDMetrics quality report)...")
    report = evaluate_quality(
        real_data=real_data,
        synthetic_data=synthetic_data,
        metadata=metadata,
        verbose=True,
    )

    overall = report.get_score()
    props = report.get_properties()

    print("\n" + "=" * 60)
    print("Quality report summary")
    print("=" * 60)
    print(f"Overall quality score (0-1 scale): {overall:.4f}  (~{overall * 100:.2f}%)")
    print("\nProperty scores (Column Shapes ~ marginal fidelity; Column Pair Trends ~ dependencies):")
    print(props.to_string(index=False))

    for prop_name in ("Column Shapes", "Column Pair Trends"):
        details = report.get_details(prop_name)
        print(f"\nDetails - {prop_name} (subset):")
        print(details.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
