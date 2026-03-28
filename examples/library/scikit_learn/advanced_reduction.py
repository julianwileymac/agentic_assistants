# requires: scikit-learn

"""
Dimensionality reduction and feature shaping: TruncatedSVD on sparse text counts,
Kernel PCA (RBF/poly), feature agglomeration, and variance thresholding.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        from sklearn.cluster import FeatureAgglomeration
        from sklearn.decomposition import KernelPCA, TruncatedSVD
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.feature_selection import VarianceThreshold
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    rng = np.random.default_rng(11)
    n_docs = 450
    vocab_tokens = [f"w{i}" for i in range(40)]
    corpus: list[str] = []
    for i in range(n_docs):
        picks = rng.choice(vocab_tokens, size=rng.integers(4, 14), replace=True)
        corpus.append(" ".join(picks))

    print("=" * 60)
    print("TruncatedSVD on sparse CountVectorizer matrix")
    print("=" * 60)
    vectorizer = CountVectorizer(max_features=120, min_df=2)
    X_sparse = vectorizer.fit_transform(corpus)
    svd = TruncatedSVD(n_components=18, random_state=11)
    X_dense_svd = svd.fit_transform(X_sparse)
    var_ratio = svd.explained_variance_ratio_.sum()
    print(f"  Sparse shape: {X_sparse.shape}")
    print(f"  Reduced shape: {X_dense_svd.shape}")
    print(f"  Sum explained variance ratio (components): {var_ratio:.4f}")

    # Dense synthetic for Kernel PCA / agglomeration / threshold
    X = rng.standard_normal((600, 24))
    X[:, :6] += 2.1 * (rng.random((600, 6)) - 0.5)
    X = StandardScaler().fit_transform(X)

    print()
    print("=" * 60)
    print("Kernel PCA - RBF and polynomial kernels")
    print("=" * 60)
    kpca_rbf = KernelPCA(
        n_components=5,
        kernel="rbf",
        gamma=0.35,
        random_state=11,
    )
    Z_rbf = kpca_rbf.fit_transform(X[:400])
    print(f"  RBF output shape (subset): {Z_rbf.shape}")

    kpca_poly = KernelPCA(
        n_components=5,
        kernel="poly",
        degree=3,
        coef0=1.0,
        gamma=0.15,
    )
    Z_poly = kpca_poly.fit_transform(X[:400])
    print(f"  Poly output shape (subset): {Z_poly.shape}")

    print()
    print("=" * 60)
    print("Feature agglomeration (Ward, 24 -> 10 merged features)")
    print("=" * 60)
    agg = FeatureAgglomeration(n_clusters=10, linkage="ward")
    X_agg = agg.fit_transform(X)
    print(f"  Transformed shape: {X_agg.shape}")
    print(f"  n_clusters: {agg.n_clusters}")

    print()
    print("=" * 60)
    print("VarianceThreshold (drop low-variance columns)")
    print("=" * 60)
    X_noisy = np.c_[X, 0.02 * rng.standard_normal((X.shape[0], 6))]
    vt = VarianceThreshold(threshold=0.05)
    X_sel = vt.fit_transform(X_noisy)
    print(f"  Before: {X_noisy.shape[1]} features")
    print(f"  After:  {X_sel.shape[1]} features (threshold=0.05)")

    print()
    print("=" * 60)
    print("Optional pipeline sketch: SVD -> scale (text -> dense workflow)")
    print("=" * 60)
    pipe = make_pipeline(
        CountVectorizer(max_features=80, min_df=2),
        TruncatedSVD(n_components=12, random_state=11),
        StandardScaler(with_mean=True),
    )
    Z_pipe = pipe.fit_transform(corpus[:200])
    print(f"  Pipeline output shape (200 docs): {Z_pipe.shape}")


if __name__ == "__main__":
    main()
