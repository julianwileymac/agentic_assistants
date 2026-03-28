# requires: sdv

"""Sequential / temporal synthetic data with PARSynthesizer (stocks + sensors)."""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from sdv.metadata import Metadata
        from sdv.sequential import PARSynthesizer
    except ImportError as exc:  # pragma: no cover
        print("Install sdv (and pandas/numpy) to run this example:", exc)
        return

    print("PARSynthesizer: synthetic multi-entity time series (prices + sensor-style readings)")
    print("-" * 60)

    rng = np.random.default_rng(42)
    rows: list[dict[str, object]] = []

    symbols = ["ACME", "GLOB", "NOVA"]
    for sym in symbols:
        base_price = float(rng.uniform(80.0, 120.0))
        for day in range(12):
            noise = rng.normal(0, 1.2)
            close = max(10.0, base_price + day * 0.35 + noise)
            volume = int(max(1000, rng.integers(8000, 22_000) + day * 100))
            sensor_temp = float(20.0 + 0.4 * day + rng.normal(0, 0.8))
            rows.append(
                {
                    "symbol": sym,
                    "day": day,
                    "close_price": round(close, 2),
                    "volume": volume,
                    "sensor_temp_c": round(sensor_temp, 2),
                }
            )

    real_data = pd.DataFrame(rows)
    print("Real (synthetic seed) sample:")
    print(real_data.head(6).to_string(index=False))

    metadata = Metadata.detect_from_dataframe(real_data, table_name="series")
    metadata.set_sequence_key("symbol")
    metadata.set_sequence_index("day")

    # Small epoch count keeps the demo fast; set verbose=True to watch loss.
    synthesizer = PARSynthesizer(
        metadata,
        epochs=8,
        cuda=False,
        verbose=False,
        enforce_rounding=False,
    )
    print("\nFitting PARSynthesizer...")
    synthesizer.fit(real_data)

    num_sequences = 5
    synthetic = synthesizer.sample(num_sequences=num_sequences)
    print(f"Sampled {num_sequences} new sequences; total rows={len(synthetic)}")

    print("\n--- Distribution check: close_price ---")
    print("real mean/std:     ", f"{real_data['close_price'].mean():.3f}", f"{real_data['close_price'].std():.3f}")
    print("synthetic mean/std:", f"{synthetic['close_price'].mean():.3f}", f"{synthetic['close_price'].std():.3f}")

    print("\n--- sensor_temp_c ---")
    print("real mean/std:     ", f"{real_data['sensor_temp_c'].mean():.3f}", f"{real_data['sensor_temp_c'].std():.3f}")
    print("synthetic mean/std:", f"{synthetic['sensor_temp_c'].mean():.3f}", f"{synthetic['sensor_temp_c'].std():.3f}")

    print("\nSynthetic preview:")
    print(synthetic.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
