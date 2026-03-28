# requires: great_expectations, pandas
"""Checkpoint-style validation against synthetic pandas data."""

from __future__ import annotations


def main() -> None:
    print("Great Expectations: validate a DataFrame and summarize results")
    print("-" * 60)
    try:
        import great_expectations as gx
        import pandas as pd
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install great-expectations pandas"
        )
        return

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "score": [10, 20, 35],
        }
    )

    context = gx.get_context()
    success = False
    result = None

    try:
        validator = context.sources.add_pandas("tmp").read_dataframe(df)
        validator.expect_column_values_to_not_be_null("id")
        validator.expect_column_values_to_be_between("score", min_value=0, max_value=30)
        result = validator.validate()
        success = bool(result.success)
    except Exception as primary_exc:
        print(f"Fluent pandas source API failed: {primary_exc}")
        try:
            from great_expectations.dataset import PandasDataset

            pds = PandasDataset(df)
            pds.expect_column_values_to_not_be_null("id")
            pds.expect_column_values_to_be_between("score", min_value=0, max_value=30)
            result = pds.validate()
            success = bool(result.success)
        except Exception as legacy_exc:
            print(f"Legacy PandasDataset path failed: {legacy_exc}")
            print(
                "Print-only outcome: with max_score=30, value 35 should fail validation.\n"
                "success=False expected."
            )
            success = False

    print(f"\nValidation success flag: {success}")
    if result is not None:
        print(f"Result type: {type(result).__name__}")
        stats = getattr(result, "statistics", None)
        if stats is not None:
            print(f"Statistics: {stats}")


if __name__ == "__main__":
    main()
