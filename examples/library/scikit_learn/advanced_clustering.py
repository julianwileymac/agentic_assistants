# requires: scikit-learn

"""
Density and spectral clustering on synthetic blobs: OPTICS, Spectral (RBF affinity),
bootstrap stability, and a compact comparison with KMeans and DBSCAN.
"""

from __future__ import annotations


def _bootstrap_label_stability(
    X,
    fit_predict_labels,
    *,
    n_bootstrap: int = 8,
    random_state: int = 0,
) -> float:
    """Mean adjusted Rand index between full-data labels and bootstrap refits (same n)."""
    import numpy as np
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.RandomState(random_state)
    labels_full = fit_predict_labels(X)
    aris: list[float] = []
    n = X.shape[0]
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        Xb = X[idx]
        labels_boot_on_idx = fit_predict_labels(Xb)
        try:
            aris.append(
                adjusted_rand_score(labels_full[idx], labels_boot_on_idx)
            )
        except ValueError:
            continue
    return float(np.mean(aris)) if aris else float("nan")


def main() -> None:
    try:
        import numpy as np
        from sklearn.cluster import (
            DBSCAN,
            KMeans,
            OPTICS,
            SpectralClustering,
        )
        from sklearn.datasets import make_blobs
        from sklearn.metrics import (
            adjusted_rand_score,
            silhouette_score,
        )
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    rng = 42
    X, y_true = make_blobs(
        n_samples=500,
        centers=4,
        n_features=12,
        cluster_std=1.1,
        random_state=rng,
    )
    X = StandardScaler().fit_transform(X)

    print("=" * 60)
    print("OPTICS (synthetic blobs)")
    print("=" * 60)
    optics = OPTICS(
        min_samples=8,
        xi=0.05,
        min_cluster_size=0.05,
        metric="euclidean",
        n_jobs=1,
    )
    y_optics = optics.fit_predict(X)
    n_clusters_optics = len(set(y_optics)) - (1 if -1 in y_optics else 0)
    print(f"  Estimated clusters (excluding noise): {n_clusters_optics}")
    print(f"  Noise points: {(y_optics == -1).sum()}")
    if n_clusters_optics > 1 and np.sum(y_optics != -1) > 1:
        mask = y_optics != -1
        sil_o = silhouette_score(X[mask], y_optics[mask])
        print(f"  Silhouette (non-noise): {sil_o:.4f}")
    mask_o = y_optics >= 0
    if mask_o.sum() > 1 and len(np.unique(y_optics[mask_o])) > 1:
        ari_o = adjusted_rand_score(y_true[mask_o], y_optics[mask_o])
        print(f"  ARI vs blob labels (non-noise only): {ari_o:.4f}")
    else:
        print("  ARI vs blob labels: n/a (insufficient clustered points)")

    print()
    print("=" * 60)
    print("Spectral clustering (affinity=rbf, n_clusters=4)")
    print("=" * 60)
    spectral = SpectralClustering(
        n_clusters=4,
        affinity="rbf",
        gamma=0.5,
        random_state=rng,
        n_jobs=1,
    )
    y_spec = spectral.fit_predict(X)
    sil_s = silhouette_score(X, y_spec)
    ari_s = adjusted_rand_score(y_true, y_spec)
    print(f"  Silhouette: {sil_s:.4f}")
    print(f"  ARI vs ground truth: {ari_s:.4f}")

    print()
    print("=" * 60)
    print("Bootstrap stability (mean ARI vs full-data clustering, 8 resamples)")
    print("=" * 60)

    def km_factory():
        km = KMeans(n_clusters=4, random_state=rng, n_init="auto")
        return km

    stab_km = _bootstrap_label_stability(
        X,
        lambda Z: km_factory().fit(Z).labels_,
        n_bootstrap=8,
        random_state=1,
    )

    def dbscan_factory():
        # Scaled blobs: eps must bridge within-cluster neighbors (~0.7–1.2 typical).
        return DBSCAN(eps=0.85, min_samples=6)

    stab_db = _bootstrap_label_stability(
        X,
        lambda Z: dbscan_factory().fit(Z).labels_,
        n_bootstrap=8,
        random_state=2,
    )

    def optics_factory():
        return OPTICS(
            min_samples=8,
            xi=0.05,
            min_cluster_size=0.05,
            metric="euclidean",
            n_jobs=1,
        )

    stab_op = _bootstrap_label_stability(
        X,
        lambda Z: optics_factory().fit(Z).labels_,
        n_bootstrap=8,
        random_state=3,
    )

    def spectral_factory():
        return SpectralClustering(
            n_clusters=4,
            affinity="rbf",
            gamma=0.5,
            random_state=rng,
            n_jobs=1,
        )

    stab_sp = _bootstrap_label_stability(
        X,
        lambda Z: spectral_factory().fit(Z).labels_,
        n_bootstrap=8,
        random_state=4,
    )

    for name, val in [
        ("KMeans", stab_km),
        ("DBSCAN", stab_db),
        ("OPTICS", stab_op),
        ("Spectral", stab_sp),
    ]:
        print(f"  {name:10s}  mean bootstrap ARI: {val:.4f}")

    print()
    print("=" * 60)
    print("Algorithm comparison (same scaled blobs)")
    print("=" * 60)

    km = KMeans(n_clusters=4, random_state=rng, n_init="auto")
    y_km = km.fit_predict(X)
    db = DBSCAN(eps=0.85, min_samples=6)
    y_db = db.fit_predict(X)

    rows: list[tuple[str, int, str, float]] = []

    def add_row(name: str, labels: np.ndarray) -> None:
        n_lab = len(set(labels)) - (1 if -1 in labels else 0)
        if len(set(labels)) > 1 and np.sum(labels != -1) > 1:
            m = labels != -1 if -1 in labels else np.ones(len(labels), dtype=bool)
            sil = silhouette_score(X[m], labels[m])
        else:
            sil = float("nan")
        ari = adjusted_rand_score(y_true, labels)
        rows.append((name, n_lab, f"{sil:.4f}" if sil == sil else "n/a", ari))

    add_row("KMeans", y_km)
    add_row("DBSCAN", y_db)
    add_row("OPTICS", y_optics)
    add_row("Spectral", y_spec)

    hdr = f"{'Algorithm':12s}  {'clusters':>8s}  {'silhouette':>10s}  {'ARI':>8s}"
    print(hdr)
    print("-" * len(hdr))
    for name, n_c, sil_s, ari in rows:
        print(f"{name:12s}  {n_c:8d}  {sil_s:>10s}  {ari:8.4f}")


if __name__ == "__main__":
    main()
