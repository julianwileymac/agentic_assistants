# requires: great_expectations, pandas
"""Great Expectations: expectation suites on a pandas DataFrame."""

from __future__ import annotations


def main() -> None:
    print("Great Expectations: build an expectation suite from a pandas DataFrame")
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
            "passenger_count": [1, 2, None, 4],
            "trip_distance": [0.8, 12.4, 3.1, 99.0],
            "fare_amount": [5.0, 22.0, 8.5, 150.0],
        }
    )
    print("Sample data (note: null passenger_count row):")
    print(df.to_string(index=False))

    context = gx.get_context()
    print(f"\nData context type: {type(context).__name__}")

    suite = None
    try:
        from great_expectations.core import ExpectationSuite
        from great_expectations.expectations.expectation_configuration import (
            ExpectationConfiguration,
        )

        suite = ExpectationSuite(expectation_suite_name="taxi_demo")
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": "passenger_count"},
            )
        )
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "trip_distance", "min_value": 0.0, "max_value": 50.0},
            )
        )
        suite.add_expectation(
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={"column": "fare_amount", "min_value": 0.0, "max_value": 100.0},
            )
        )
    except Exception as exc:
        print(f"Could not build ExpectationSuite via configuration API: {exc}")
        return

    print("\nExpectations in suite:")
    for exp in suite.expectations:
        print(f"  - {exp.expectation_type} {exp.kwargs}")

    # Optional: attach suite to context (ephemeral contexts may vary by GX version)
    try:
        context.add_expectation_suite(expectation_suite=suite)
        print("\nSuite registered on context as 'taxi_demo'.")
    except Exception as exc:
        print(f"\nadd_expectation_suite not applied (OK for demo): {exc}")


if __name__ == "__main__":
    main()
