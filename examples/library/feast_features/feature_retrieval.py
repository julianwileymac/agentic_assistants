# requires: feast, pandas
"""get_historical_features and get_online_features usage patterns."""

from __future__ import annotations


def main() -> None:
    print("Feast retrieval: historical (training) vs online (serving)")
    print("-" * 60)

    try:
        import pandas as pd
        from feast import FeatureStore
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install feast pandas"
        )
        _demo_without_feast()
        return

    print(
        "Entity DataFrame: each row is an entity id (and optional timestamp for historical).\n"
        "Example columns: driver_id, event_timestamp (for point-in-time joins).\n"
    )
    entity_df = pd.DataFrame(
        {
            "driver_id": [1001, 1002, 1003],
            "event_timestamp": pd.to_datetime(
                ["2024-06-01 10:00:00", "2024-06-01 10:05:00", "2024-06-01 10:10:00"]
            ),
        }
    )
    print("Sample entity_df:\n", entity_df.to_string(index=False), sep="")

    print(
        "\n--- get_historical_features (training / batch) ---\n"
        "Joins labels + features at timestamps in entity_df (no peeking into the future).\n"
        "Typical call:\n"
        "  fs = FeatureStore(repo_path='./feature_repo')\n"
        "  training_df = fs.get_historical_features(\n"
        "      entity_df=entity_df,\n"
        "      features=[\n"
        "          'driver_stats:conv_rate',\n"
        "          'driver_stats:acc_rate',\n"
        "          'driver_stats:trips_today',\n"
        "      ],\n"
        "  )\n"
    )

    print(
        "--- get_online_features (low-latency inference) ---\n"
        "Looks up latest materialized values for live entity keys.\n"
        "Typical call:\n"
        "  online_input = {'driver_id': [1001, 1002]}\n"
        "  resp = fs.get_online_features(\n"
        "      features=[\n"
        "          'driver_stats:conv_rate',\n"
        "          'driver_stats:acc_rate',\n"
        "      ],\n"
        "      entity_rows=online_input,\n"
        "  )\n"
        "  # resp.to_dict() -> columnar feature vectors\n"
    )

    print(
        "\nFeatureStore symbol resolved:", FeatureStore,
        "\n(No live FeatureStore repo in this demo — no RPC to online/offline backends.)"
    )


def _demo_without_feast() -> None:
    print(
        "Without Feast, the same contracts apply:\n"
        "  - Historical: wide table with correct timestamps for each label row.\n"
        "  - Online: feature vector keyed by entity id for model input.\n"
    )


if __name__ == "__main__":
    main()
