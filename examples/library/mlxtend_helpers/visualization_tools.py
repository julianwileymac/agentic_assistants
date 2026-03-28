# requires: mlxtend scikit-learn

"""
Decision-region grids, confusion matrices, and learning curves using mlxtend and sklearn.

Uses 2D synthetic data. Decision regions are summarized as printed grid coordinates and
predicted labels (no GUI). Confusion matrix values come from sklearn; mlxtend's
plot_confusion_matrix is the usual visualization hook. Learning curves use sklearn.
"""

from __future__ import annotations


def main() -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import confusion_matrix
        from sklearn.model_selection import learning_curve, train_test_split
        from sklearn.svm import SVC
        from mlxtend.plotting import plot_confusion_matrix
    except ImportError as exc:  # pragma: no cover
        print("Install mlxtend, scikit-learn, and matplotlib to run this example:", exc)
        return

    rng = 3
    X, y = make_classification(
        n_samples=400,
        n_features=2,
        n_redundant=0,
        n_informative=2,
        n_clusters_per_class=1,
        random_state=rng,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=rng, stratify=y
    )

    clf = SVC(kernel="linear", random_state=rng)
    clf.fit(X_train, y_train)

    print("=" * 60)
    print("Decision region concept - grid over feature space (2D synthetic)")
    print("=" * 60)
    x_min, x_max = float(X[:, 0].min() - 0.5), float(X[:, 0].max() + 0.5)
    y_min, y_max = float(X[:, 1].min() - 0.5), float(X[:, 1].max() + 0.5)
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, 25),
        np.linspace(y_min, y_max, 25),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]
    Z = clf.predict(grid).reshape(xx.shape)
    flat_xy = grid[:12]
    flat_z = Z.ravel()[:12]
    print("  Axis ranges: x in [{:.3f}, {:.3f}], y in [{:.3f}, {:.3f}]".format(
        x_min, x_max, y_min, y_max
    ))
    print("  Sample (x, y) grid points and predicted class (first 12):")
    for (a, b), c in zip(flat_xy, flat_z):
        print(f"    ({a:+.3f}, {b:+.3f}) -> class {int(c)}")

    print()
    print("=" * 60)
    print("Confusion matrix (mlxtend.plotting.plot_confusion_matrix + Agg figure)")
    print("=" * 60)
    y_pred = clf.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    print("  Matrix (rows=true, cols=pred):\n", cm)
    out = plot_confusion_matrix(conf_mat=cm, figsize=(4, 4))
    fig = out[0] if isinstance(out, tuple) else out
    if fig is not None:
        plt.close(fig)
    else:
        plt.close("all")
    print("  (Figure built headlessly with matplotlib 'Agg'; values printed above.)")

    print()
    print("=" * 60)
    print("Learning curves (sklearn.model_selection.learning_curve)")
    print("=" * 60)
    lr = LogisticRegression(max_iter=500, random_state=rng)
    train_sizes, train_scores, val_scores = learning_curve(
        lr,
        X,
        y,
        train_sizes=np.linspace(0.2, 1.0, 5),
        cv=5,
        scoring="accuracy",
        random_state=rng,
    )
    train_mean = train_scores.mean(axis=1)
    val_mean = val_scores.mean(axis=1)
    print("  Train sizes:", train_sizes)
    print("  Mean train accuracy:", np.round(train_mean, 4))
    print("  Mean CV accuracy:   ", np.round(val_mean, 4))


if __name__ == "__main__":
    main()
