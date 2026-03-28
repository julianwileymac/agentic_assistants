# requires: sdv, pandas

"""Single-table synthesis with SDV GaussianCopulaSynthesizer: fit, sample, compare stats."""

from __future__ import annotations


def _print_compare_stats(original, synthetic, label: str) -> None:
    print(f"\n--- {label} (original) ---")
    print(original.to_string())
    print(f"\n--- {label} (synthetic) ---")
    print(synthetic.to_string())


def main() -> None:
    try:
        import pandas as pd
        from sdv.metadata import SingleTableMetadata
        from sdv.single_table import GaussianCopulaSynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv and pandas to run this example:", exc)
        return

    print("Building sample employee table (name, age, salary, department)...")
    employees = pd.DataFrame(
        {
            "name": [
                "Ada Lovelace",
                "Grace Hopper",
                "Alan Turing",
                "Katherine Johnson",
                "Donald Knuth",
                "Barbara Liskov",
                "Edsger Dijkstra",
                "Margaret Hamilton",
                "Ken Thompson",
                "Frances Allen",
            ],
            "age": [36, 42, 41, 44, 45, 38, 52, 40, 48, 46],
            "salary": [118_000, 132_000, 95_000, 140_000, 125_000, 150_000, 88_000, 160_000, 200_000, 135_000],
            "department": [
                "Engineering",
                "Engineering",
                "Research",
                "Research",
                "Engineering",
                "Engineering",
                "Research",
                "Engineering",
                "Engineering",
                "Research",
            ],
        }
    )

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(employees)
    # Names are unique in this toy table; detection may label them as ``id``. Treat as categorical.
    if getattr(metadata, "primary_key", None) == "name":
        metadata.remove_primary_key()
    metadata.update_column("name", sdtype="categorical")

    print("\nDetected metadata (columns / sdtypes):")
    for col, meta in metadata.columns.items():
        print(f"  {col}: {meta.get('sdtype')}")

    synthesizer = GaussianCopulaSynthesizer(metadata, enforce_min_max_values=True)
    print("\nFitting GaussianCopulaSynthesizer...")
    synthesizer.fit(employees)

    n_synth = 500
    print(f"\nSampling {n_synth} synthetic rows...")
    synthetic = synthesizer.sample(num_rows=n_synth)

    print("\n" + "=" * 60)
    print("ORIGINAL vs SYNTHETIC - summary statistics")
    print("=" * 60)

    orig_num = employees[["age", "salary"]].describe()
    synth_num = synthetic[["age", "salary"]].describe()
    _print_compare_stats(orig_num, synth_num, "Numerical (age, salary)")

    orig_dept = employees["department"].value_counts(normalize=True).sort_index()
    synth_dept = synthetic["department"].value_counts(normalize=True).sort_index()
    _print_compare_stats(orig_dept, synth_dept, "Department distribution (proportion)")

    print("\nSample synthetic rows (first 5):")
    print(synthetic.head().to_string(index=False))


if __name__ == "__main__":
    main()
