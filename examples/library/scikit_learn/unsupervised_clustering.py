# requires: scikit-learn

"""
KMeans and DBSCAN on synthetic blobs: silhouette, elbow (inertia), assignments.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.cluster import DBSCAN, KMeans
        from sklearn.datasets import make_blobs
        from sklearn.metrics import silhouette_score
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    rng_seed = 11
    X, y_true = make_blobs(
        n_samples=600,
        centers=4,
        n_features=2,
        cluster_std=0.85,
        random_state=rng_seed,
    )

    print("=" * 60)
    print("Elbow method: KMeans inertia for k = 2..10")
    print("=" * 60)
    inertias: list[float] = []
    for k in range(2, 11):
        km = KMeans(n_clusters=k, n_init="auto", random_state=rng_seed)
        km.fit(X)
        inertias.append(float(km.inertia_))
        print(f"  k={k:2d}  inertia={km.inertia_:10.2f}")

    print()
    print("=" * 60)
    print("KMeans (k=4, matches ground-truth centers)")
    print("=" * 60)
    kmeans = KMeans(n_clusters=4, n_init="auto", random_state=rng_seed)
    labels_km = kmeans.fit_predict(X)
    sil_km = silhouette_score(X, labels_km)
    print(f"  Silhouette score: {sil_km:.4f}")
    print(f"  Cluster sizes: {[int((labels_km == c).sum()) for c in range(4)]}")
    print(f"  First 12 assignments: {labels_km[:12]}")

    print()
    print("=" * 60)
    print("DBSCAN (eps=0.5, min_samples=8)")
    print("=" * 60)
    db = DBSCAN(eps=0.5, min_samples=8)
    labels_db = db.fit_predict(X)
    n_clusters_db = len(set(labels_db)) - (1 if -1 in labels_db else 0)
    n_noise = int((labels_db == -1).sum())
    mask_labeled = labels_db >= 0
    if mask_labeled.sum() > 1 and n_clusters_db > 1:
        sil_db = silhouette_score(X[mask_labeled], labels_db[mask_labeled])
        print(f"  Silhouette (non-noise): {sil_db:.4f}")
    else:
        print("  Silhouette (non-noise): n/a (too few clusters or points)")
    print(f"  Estimated clusters: {n_clusters_db}")
    print(f"  Noise points: {n_noise}")
    print(f"  First 12 assignments: {labels_db[:12]}")


if __name__ == "__main__":
    main()
