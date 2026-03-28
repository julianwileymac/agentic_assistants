# requires: hdbscan umap-learn scikit-learn

"""
End-to-end pipeline: UMAP dimensionality reduction then HDBSCAN clustering.

Synthetic blobs in R^40, UMAP to 2D, then HDBSCAN; silhouette is computed on the reduced
space against discovered labels (excluding noise where applicable).
"""

from __future__ import annotations


def main() -> None:
    try:
        import hdbscan
        import numpy as np
        from sklearn.datasets import make_blobs
        from sklearn.metrics import adjusted_rand_score, silhouette_score
        from sklearn.preprocessing import StandardScaler
        from umap import UMAP
    except ImportError as exc:  # pragma: no cover
        print("Install hdbscan, umap-learn, and scikit-learn to run this example:", exc)
        return

    rng = 44
    X, y_true = make_blobs(
        n_samples=1500,
        n_features=40,
        centers=5,
        cluster_std=1.2,
        random_state=rng,
    )
    X = StandardScaler().fit_transform(X)

    print("=" * 60)
    print("Step 1 - UMAP to 2D (unsupervised)")
    print("=" * 60)
    umap = UMAP(
        n_neighbors=30,
        min_dist=0.05,
        n_components=2,
        random_state=rng,
    )
    X_2d = umap.fit_transform(X)
    print(f"  Input shape: {X.shape} -> reduced: {X_2d.shape}")

    print()
    print("=" * 60)
    print("Step 2 - HDBSCAN on reduced coordinates")
    print("=" * 60)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=25, min_samples=5)
    labels = clusterer.fit_predict(X_2d)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))
    print(f"  Detected clusters (excl. noise): {n_clusters}")
    print(f"  Noise count: {n_noise}")

    print()
    print("=" * 60)
    print("Step 3 - Silhouette on reduced space")
    print("=" * 60)
    mask = labels != -1
    if mask.sum() > 1 and n_clusters > 1:
        sil = float(silhouette_score(X_2d[mask], labels[mask]))
        print(f"  Silhouette (non-noise, 2D): {sil:.4f}")
    else:
        print("  Silhouette not defined (too few clustered points or single cluster).")

    ari = adjusted_rand_score(y_true, labels)
    print(f"  ARI vs blob labels (includes noise as own class in ARI): {ari:.4f}")

    print()
    print("=" * 60)
    print("Full workflow summary")
    print("=" * 60)
    print("  1) Scale high-dimensional blobs")
    print("  2) UMAP to 2D for density-friendly cluster geometry")
    print("  3) HDBSCAN -> arbitrary shapes + explicit noise")
    print("  4) Silhouette on 2D embedding to judge separation of kept points")


if __name__ == "__main__":
    main()
