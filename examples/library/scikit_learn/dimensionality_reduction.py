# requires: scikit-learn

"""
PCA and t-SNE on high-dimensional synthetic classification data.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.datasets import make_classification
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    X, y = make_classification(
        n_samples=600,
        n_features=40,
        n_informative=15,
        n_redundant=10,
        n_clusters_per_class=2,
        random_state=0,
    )

    print("=" * 60)
    print("PCA (n_components=8)")
    print("=" * 60)
    pca = PCA(n_components=8, random_state=0)
    X_pca = pca.fit_transform(X)
    evr = pca.explained_variance_ratio_
    print(f"  Explained variance ratio (per component): {evr.round(4)}")
    print(f"  Cumulative explained variance: {evr.cumsum().round(4)}")
    print(f"  Transformed shape: {X_pca.shape}")
    print(
        "  Transformed summary (mean/std per dim, first 4): "
        f"means={X_pca[:, :4].mean(axis=0).round(4)}, "
        f"stds={X_pca[:, :4].std(axis=0).round(4)}"
    )

    print()
    print("=" * 60)
    print("t-SNE (n_components=2, perplexity=30)")
    print("=" * 60)
    tsne = TSNE(
        n_components=2,
        perplexity=30,
        learning_rate="auto",
        init="pca",
        random_state=0,
    )
    X_tsne = tsne.fit_transform(X_pca[:, :6])
    print(f"  Input to t-SNE: {X_pca[:, :6].shape} (first 6 PCA dims for speed)")
    print(f"  Output shape: {X_tsne.shape}")
    print(
        "  Coordinate ranges: "
        f"x=[{X_tsne[:, 0].min():.3f}, {X_tsne[:, 0].max():.3f}], "
        f"y=[{X_tsne[:, 1].min():.3f}, {X_tsne[:, 1].max():.3f}]"
    )
    print(
        "  Per-class means (dim1, dim2): "
        + ", ".join(
            f"class {c}=({X_tsne[y == c, 0].mean():.3f}, {X_tsne[y == c, 1].mean():.3f})"
            for c in sorted(set(y.tolist()))
        )
    )


if __name__ == "__main__":
    main()
