# requires: river, numpy

"""
Synthetic stream with a sudden shift; ADWIN drift detection.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        from river import drift
    except ImportError as exc:  # pragma: no cover
        print("Install river and numpy to run this example:", exc)
        return

    rng = np.random.default_rng(7)
    n_before = 1200
    n_after = 1200
    # Phase A: N(0, 1); Phase B: N(2.5, 1) — clear mean shift
    stream = np.concatenate(
        [
            rng.normal(0.0, 1.0, size=n_before),
            rng.normal(2.5, 1.0, size=n_after),
        ]
    )

    adwin = drift.ADWIN(delta=0.002)

    print("=" * 60)
    print("ADWIN on univariate stream (mean shift at t=1200)")
    print("=" * 60)

    drift_idx: int | None = None
    for t, x in enumerate(stream):
        adwin.update(float(x))
        if adwin.drift_detected and drift_idx is None:
            drift_idx = t
            print(f"  Drift detected at index: {t} (value={x:.4f})")
            print(f"  ADWIN width (est. window): {adwin.width}")

    if drift_idx is None:
        print("  No drift flagged (try lowering delta or increasing shift).")
    else:
        print(f"  True shift starts at index: {n_before}")
        print(f"  Detection lag: {drift_idx - n_before} steps")

    print(f"  Stream mean (first half): {stream[:n_before].mean():.4f}")
    print(f"  Stream mean (second half): {stream[n_before:].mean():.4f}")


if __name__ == "__main__":
    main()
