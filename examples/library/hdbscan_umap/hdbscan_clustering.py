# requires: hdbscan umap-learn scikit-learn

"""
HDBSCAN on synthetic blobs: tuning, soft membership, outlier scores, and KMeans comparison.

Uses sklearn.datasets.make_blobs; explores min_cluster_size, probabilities, and outlier
scores where available, then compares cluster quality to KMeans on the same data.
"""

from __future__ import annotations


def main() -> None:
    try:
        import hdbscan
        import numpy as np
        from sklearn.cluster import KMeans
        from sklearn.datasets import make_blobs
        from sklearn.metrics import adjusted_rand_score, silhouette_score
    except ImportError as exc:  # pragma: no cover
        print("Install hdbscan, umap-learn, and scikit-learn to run this example:", exc)
        return

    rng = 17
    X, y_true = make_blobs(
        n_samples=800,
        centers=4,
        cluster_std=0.85,
        random_state=rng,
    )

    print("=" * 60)
    print("HDBSCAN - min_cluster_size tuning (same random blobs)")
    print("=" * 60)
    for mcs in (5, 15, 40):
        clusterer = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=3)
        labels = clusterer.fit_predict(X)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = int(np.sum(labels == -1))
        mask = labels != -1
        sil = (
            float(silhouette_score(X[mask], labels[mask]))
            if mask.sum() > 1 and n_clusters > 1
            else float("nan")
        )
        ari = adjusted_rand_score(y_true, labels)
        print(
            f"  min_cluster_size={mcs}: clusters={n_clusters}, noise={n_noise}, "
            f"silhouette={sil:.4f}, ARI={ari:.4f}"
        )

    print()
    print("=" * 60)
    print("HDBSCAN - soft clustering probabilities and outlier scores")
    print("=" * 60)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=4, prediction_data=True)
    labels = clusterer.fit_predict(X)
    probs = getattr(clusterer, "probabilities_", None)
    if probs is not None:
        print(f"  probabilities_ sample (first 8): {np.round(probs[:8], 3)}")
        print(f"  mean probability (non-noise): {float(np.mean(probs[labels != -1])):.4f}")
    else:  # pragma: no cover
        print("  probabilities_ not available for this hdbscan build.")

    out = getattr(clusterer, "outlier_scores_", None)
    if out is not None:
        print(f"  outlier_scores_ sample (first 8): {np.round(out[:8], 3)}")
        noise_mask = labels == -1
        if noise_mask.any():
            print(f"  mean outlier score (noise points): {float(np.mean(out[noise_mask])):.4f}")
    else:
        print("  outlier_scores_ not available; using inverse probability as proxy where possible.")
        if probs is not None:
            print(f"  1 - prob sample (first 8): {np.round(1.0 - probs[:8], 3)}")

    if hasattr(hdbscan, "all_points_membership_vectors"):
        mv = hdbscan.all_points_membership_vectors(clusterer)
        print(f"  soft membership matrix shape: {mv.shape} (rows=samples, cols=clusters)")
        print(f"  row sums (first 5): {np.round(mv[:5].sum(axis=1), 3)}")

    print()
    print("=" * 60)
    print("Comparison: HDBSCAN vs KMeans (k = 4)")
    print("=" * 60)
    km = KMeans(n_clusters=4, n_init="auto", random_state=rng)
    y_km = km.fit_predict(X)
    hdb = hdbscan.HDBSCAN(min_cluster_size=15, min_samples=4)
    y_hdb = hdb.fit_predict(X)
    mask_h = y_hdb != -1
    sil_km = silhouette_score(X, y_km)
    sil_hdb = (
        silhouette_score(X[mask_h], y_hdb[mask_h]) if mask_h.sum() > 1 else float("nan")
    )
    print(f"  KMeans silhouette (all points):     {sil_km:.4f}")
    print(f"  HDBSCAN silhouette (non-noise):     {sil_hdb:.4f}")
    print(f"  KMeans ARI vs ground-truth labels:  {adjusted_rand_score(y_true, y_km):.4f}")
    print(f"  HDBSCAN ARI vs ground-truth labels: {adjusted_rand_score(y_true, y_hdb):.4f}")
    print("  HDBSCAN exposes noise (-1); KMeans forces every point into a cluster.")


if __name__ == "__main__":
    main()
