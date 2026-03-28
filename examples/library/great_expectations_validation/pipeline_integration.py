# requires: great_expectations, pandas
"""Use Great Expectations as a pass/fail gate inside a data pipeline."""

from __future__ import annotations


def validate_batch(df):  # noqa: ANN001
    """Return True if dataframe passes GX checks, else False."""
    try:
        import great_expectations as gx
    except ImportError:
        return False

    context = gx.get_context()
    try:
        validator = context.sources.add_pandas("pipeline_tmp").read_dataframe(df)
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_be_between("amount", min_value=0, max_value=1_000_000)
        res = validator.validate()
        return bool(res.success)
    except Exception:
        try:
            from great_expectations.dataset import PandasDataset

            pds = PandasDataset(df)
            pds.expect_column_values_to_not_be_null("id")
            pds.expect_column_values_to_be_between("amount", min_value=0, max_value=1_000_000)
            return bool(pds.validate().success)
        except Exception:
            return False


def main() -> None:
    print("Pipeline gate: extract → validate (GX) → transform → load")
    print("-" * 60)
    try:
        import pandas as pd
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install pandas great-expectations"
        )
        return

    good = pd.DataFrame({"id": [1, 2], "amount": [10.0, 20.0]})
    bad = pd.DataFrame({"id": [1, None], "amount": [10.0, 2_000_000.0]})

    print("Batch A (should pass):")
    print(good.to_string(index=False))
    print(f"  validate_batch -> {validate_batch(good)}")

    print("\nBatch B (null id + amount too large — should fail):")
    print(bad.to_string(index=False))
    print(f"  validate_batch -> {validate_batch(bad)}")

    print(
        "\nDownstream steps run only when validate_batch is True;\n"
        "otherwise the pipeline logs, quarantines, or alerts operators.\n"
    )


if __name__ == "__main__":
    main()
