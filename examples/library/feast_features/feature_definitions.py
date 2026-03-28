# requires: feast
"""Feast entities, feature views, feature services, Field, and ValueType."""

from __future__ import annotations

from datetime import timedelta


def main() -> None:
    print("Feast feature definitions: Entity, FeatureView, FeatureService, Field, ValueType")
    print("-" * 60)
    try:
        from feast import Entity, FeatureService, FeatureView, Field, FileSource
        from feast.types import Float32, Int64, UnixTimestamp
    except ImportError:
        print(
            "Missing dependency. Install with:\n"
            "  pip install feast"
        )
        return

    try:
        from feast.value_type import ValueType
    except ImportError:
        ValueType = None  # type: ignore[misc, assignment]

    driver = Entity(
        name="driver",
        join_keys=["driver_id"],
        description="Driver identifier for ride-hailing features",
    )

    # Offline source path is declarative; materialization would populate real data.
    source = FileSource(
        path="data/driver_stats.parquet",
        timestamp_field="event_timestamp",
    )

    driver_stats_fv = FeatureView(
        name="driver_stats",
        entities=[driver],
        ttl=timedelta(days=2),
        schema=[
            Field(name="conv_rate", dtype=Float32, description="Trip conversion rate"),
            Field(name="acc_rate", dtype=Float32, description="Acceptance rate"),
            Field(name="trips_today", dtype=Int64),
            Field(name="last_seen", dtype=UnixTimestamp),
        ],
        online=True,
        source=source,
        tags={"team": "ml-platform"},
    )

    promo_fv = FeatureView(
        name="driver_promo",
        entities=[driver],
        ttl=timedelta(hours=6),
        schema=[Field(name="promo_active", dtype=Float32)],
        source=source,
    )

    training_fs = FeatureService(
        name="driver_training_service",
        features=[driver_stats_fv, promo_fv],
    )

    print("Entity:", driver.name, "join_keys=", driver.join_keys)
    print("FeatureView:", driver_stats_fv.name)
    for f in driver_stats_fv.schema:
        print(f"  Field {f.name!r} dtype={f.dtype}")
    print("FeatureService:", training_fs.name)
    print("Features in service:", [fv.name for fv in training_fs.features])

    print("\nValueType enum examples (Feast protobuf-backed types):")
    if ValueType is None:
        print("  (ValueType not available in this Feast build — see feast.value_type / docs.)")
    else:
        for name in ("FLOAT", "DOUBLE", "INT64", "STRING", "BOOL"):
            if hasattr(ValueType, name):
                print(f"  ValueType.{name} =", getattr(ValueType, name))

    print("\nNote: apply() these objects with FeatureStore(repo_path=...) to persist to the registry.")


if __name__ == "__main__":
    main()
