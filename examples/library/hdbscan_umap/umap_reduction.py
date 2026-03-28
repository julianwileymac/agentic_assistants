# requires: hdbscan umap-learn scikit-learn

"""
UMAP vs PCA vs t-SNE on high-dimensional synthetic data; n_neighbors / min_dist / supervised UMAP.

Generates a supervised classification dataset in R^50, projects to 2D with each method,
and reports 2D silhouette scores (geometry-only sanity check, not a gold metric).
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.manifold import TSNE
        from sklearn.metrics import silhouette_score
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from umap import UMAP
        from sklearn.decomposition import PCA
    except ImportError as exc:  # pragma: no cover
        print("Install hdbscan, umap-learn, and scikit-learn to run this example:", exc)
        return

    rng = 99
    X, y = make_classification(
        n_samples=1200,
        n_features=50,
        n_informative=25,
        n_redundant=10,
        random_state=rng,
    )
    X = StandardScaler().fit_transform(X)
    X_train, X_test, y_train, _ = train_test_split(
        X, y, test_size=0.25, random_state=rng, stratify=y
    )

    def silhouette_2d(Z: np.ndarray, labels: np.ndarray) -> float:
        if len(set(labels)) < 2:
            return float("nan")
        return float(silhouette_score(Z, labels))

    print("=" * 60)
    print("UMAP - n_neighbors and min_dist (unsupervised, train-only fit)")
    print("=" * 60)
    for n_neighbors in (5, 25, 80):
        for min_dist in (0.0, 0.1, 0.5):
            u = UMAP(
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                n_components=2,
                random_state=rng,
            )
            Z_tr = u.fit_transform(X_train)
            Z_te = u.transform(X_test)
            sil = silhouette_2d(Z_tr, y_train)
            print(
                f"  n_neighbors={n_neighbors:3d}, min_dist={min_dist:.1f} -> "
                f"2D train silhouette={sil:.4f}, test shape={Z_te.shape}"
            )

    print()
    print("=" * 60)
    print("Supervised UMAP (class labels as target; full matrix for clarity)")
    print("=" * 60)
    u_sup = UMAP(
        n_neighbors=30,
        min_dist=0.1,
        n_components=2,
        random_state=rng,
        target_metric="categorical",
    )
    Zs = u_sup.fit_transform(X, y)
    print(f"  2D embedding shape: {Zs.shape}")
    print(f"  2D silhouette (class labels): {silhouette_2d(Zs, y):.4f}")

    print()
    print("=" * 60)
    print("PCA vs t-SNE vs UMAP (2 components / 2D)")
    print("=" * 60)
    Z_pca = PCA(n_components=2, random_state=rng).fit_transform(X_train)
    Z_umap = UMAP(n_neighbors=30, min_dist=0.1, n_components=2, random_state=rng).fit_transform(
        X_train
    )
    tsne = TSNE(
        n_components=2,
        perplexity=30,
        learning_rate="auto",
        init="pca",
        random_state=rng,
    )
    Z_tsne = tsne.fit_transform(X_train)

    print(f"  PCA   train 2D silhouette: {silhouette_2d(Z_pca, y_train):.4f}")
    print(f"  t-SNE train 2D silhouette: {silhouette_2d(Z_tsne, y_train):.4f}")
    print(f"  UMAP  train 2D silhouette: {silhouette_2d(Z_umap, y_train):.4f}")
    print("  (Linear PCA preserves global structure; t-SNE emphasizes local neighborhoods;")
    print("   UMAP balances local/global and scales better than t-SNE on large n.)")


if __name__ == "__main__":
    main()
