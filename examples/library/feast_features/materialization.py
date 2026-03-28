# requires: feast
"""Materialization: moving features from offline store into the online store."""

from __future__ import annotations


def main() -> None:
    print("Feast materialization: offline vs online stores (conceptual demo)")
    print("-" * 60)

    print(
        "Offline store:\n"
        "  - Holds historical feature data (often warehouse / parquet files).\n"
        "  - Used for training labels via get_historical_features (point-in-time correct joins).\n"
    )
    print(
        "Online store:\n"
        "  - Low-latency key-value style store (e.g. Redis, DynamoDB, SQLite) for serving.\n"
        "  - Populated by materialize(), which computes latest feature values per entity.\n"
    )

    try:
        from feast import FeatureStore
    except ImportError:
        print(
            "Feast not installed — showing API pattern only.\n"
            "  pip install feast\n"
        )
        print(
            "Typical flow with a real repo:\n"
            "  store = FeatureStore(repo_path='./feature_repo')\n"
            "  store.materialize(start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2))\n"
            "  # or incremental:\n"
            "  store.materialize_incremental(end_date=datetime.utcnow())\n"
        )
        return

    print(
        "FeatureStore class is available. Without a configured feature_repo on disk,\n"
        "this script does not call materialize() (that needs registry + sources).\n"
    )
    print(f"FeatureStore: {FeatureStore}")
    print(
        "\nWhen infra exists, materialize writes the latest feature rows for each entity\n"
        "from batch/offline computation into the online store so get_online_features is fast."
    )


if __name__ == "__main__":
    main()
