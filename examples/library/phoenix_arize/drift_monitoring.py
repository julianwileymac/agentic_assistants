# requires: arize-phoenix

"""
Embedding drift and data-quality style monitoring with synthetic vectors.

Computes simple reference-vs-production statistics (centroid shift, mean cosine similarity)
and demonstrates threshold-based alerting patterns used before wiring to Phoenix dashboards.
"""

from __future__ import annotations


def main() -> None:
    try:
        import phoenix as px
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        print("Install arize-phoenix (and numpy) to run this example:", exc)
        return

    rng = np.random.default_rng(2026)
    dim = 32
    n_ref, n_prod = 500, 500

    # Reference: zero-mean Gaussian embeddings (simulating a stable corpus).
    ref = rng.standard_normal((n_ref, dim)).astype(np.float64)
    ref /= np.linalg.norm(ref, axis=1, keepdims=True) + 1e-12

    # Production: same distribution + small shift + slightly higher noise (simulating drift).
    shift = rng.standard_normal(dim)
    shift = 0.15 * shift / (np.linalg.norm(shift) + 1e-12)
    prod = ref[:n_prod] + shift + 0.05 * rng.standard_normal((n_prod, dim))
    prod /= np.linalg.norm(prod, axis=1, keepdims=True) + 1e-12

    mu_ref = ref.mean(axis=0)
    mu_prod = prod.mean(axis=0)
    l2_shift = float(np.linalg.norm(mu_prod - mu_ref))

    sims = np.sum(mu_ref * mu_prod) / (
        (np.linalg.norm(mu_ref) + 1e-12) * (np.linalg.norm(mu_prod) + 1e-12)
    )

    # Pairwise sample similarity distribution (reference vs shuffled prod sample).
    idx = rng.permutation(n_prod)[:200]
    pair_cos = np.sum(ref[idx] * prod[idx], axis=1)
    mean_pair = float(np.mean(pair_cos))
    p10_pair = float(np.percentile(pair_cos, 10))

    print("=" * 60)
    print("Synthetic embedding drift (normalized random vectors)")
    print("=" * 60)
    print(f"  phoenix import OK: {px.__name__} {getattr(px, '__version__', '')}".strip())
    print(f"  dim={dim}, n_ref={n_ref}, n_prod={n_prod}")
    print(f"  ||E[prod] - E[ref]||_2 (centroid L2 shift): {l2_shift:.4f}")
    print(f"  cosine(E[ref], E[prod]): {sims:.4f}")
    print(f"  mean cosine(ref_i, prod_i) on 200 pairs: {mean_pair:.4f}")
    print(f"  10th percentile pair cosine: {p10_pair:.4f}")

    print()
    print("=" * 60)
    print("Alert thresholds (example policy on mock metrics)")
    print("=" * 60)
    centroid_threshold = 0.12
    cosine_threshold = 0.985
    tail_threshold = 0.75

    alerts: list[str] = []
    if l2_shift > centroid_threshold:
        alerts.append(f"centroid_shift>{centroid_threshold}")
    if sims < cosine_threshold:
        alerts.append(f"mean_cosine<{cosine_threshold}")
    if p10_pair < tail_threshold:
        alerts.append(f"p10_pair_cosine<{tail_threshold}")

    if alerts:
        print("  TRIGGERED:", ", ".join(alerts))
    else:
        print("  No alerts on this draw (tighten thresholds to force a trigger).")

    print()
    print("Data quality checks (vector side):")
    nan_ref = int(np.isnan(ref).sum())
    nan_prod = int(np.isnan(prod).sum())
    zero_norm = int((np.linalg.norm(prod, axis=1) < 1e-9).sum())
    print(f"  NaN count ref/prod: {nan_ref}/{nan_prod}")
    print(f"  Near-zero prod norms: {zero_norm}")

    print()
    print("Phoenix mapping:")
    print("  - Log embedding spans or offline batch metrics to Phoenix for drift views.")
    print("  - Use UMAP / histogram panels on embedding columns plus alert rules in your platform.")
    print("  - Keep thresholds versioned next to the embedding model id and retrain schedule.")


if __name__ == "__main__":
    main()
