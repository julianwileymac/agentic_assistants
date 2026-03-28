# requires: mlxtend scikit-learn

"""
Sequential and exhaustive feature selection with mlxtend on synthetic classification data.

Compares forward/backward sequential selection and exhaustive search; reports chosen feature
indices and hold-out accuracy for each strategy.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import train_test_split
        from mlxtend.feature_selection import (
            ExhaustiveFeatureSelector,
            SequentialFeatureSelector,
        )
    except ImportError as exc:  # pragma: no cover
        print("Install mlxtend and scikit-learn to run this example:", exc)
        return

    rng = 42
    X, y = make_classification(
        n_samples=600,
        n_features=8,
        n_informative=5,
        n_redundant=1,
        random_state=rng,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=rng, stratify=y
    )

    base = LogisticRegression(max_iter=500, random_state=rng)

    print("=" * 60)
    print("SequentialFeatureSelector - forward (k_features=4)")
    print("=" * 60)
    sfs_fwd = SequentialFeatureSelector(
        base,
        k_features=4,
        forward=True,
        floating=False,
        scoring="accuracy",
        cv=4,
        n_jobs=1,
    )
    sfs_fwd.fit(X_train, y_train)
    fwd_idx = tuple(sfs_fwd.k_feature_idx_)
    X_tr_f, X_te_f = X_train[:, fwd_idx], X_test[:, fwd_idx]
    base.fit(X_tr_f, y_train)
    acc_fwd = accuracy_score(y_test, base.predict(X_te_f))
    print(f"  Selected feature indices: {fwd_idx}")
    print(f"  Test accuracy (subset): {acc_fwd:.4f}")

    print()
    print("=" * 60)
    print("SequentialFeatureSelector - backward (k_features=4)")
    print("=" * 60)
    sfs_bwd = SequentialFeatureSelector(
        base,
        k_features=4,
        forward=False,
        floating=False,
        scoring="accuracy",
        cv=4,
        n_jobs=1,
    )
    sfs_bwd.fit(X_train, y_train)
    bwd_idx = tuple(sfs_bwd.k_feature_idx_)
    X_tr_b, X_te_b = X_train[:, bwd_idx], X_test[:, bwd_idx]
    base.fit(X_tr_b, y_train)
    acc_bwd = accuracy_score(y_test, base.predict(X_te_b))
    print(f"  Selected feature indices: {bwd_idx}")
    print(f"  Test accuracy (subset): {acc_bwd:.4f}")

    print()
    print("=" * 60)
    print("ExhaustiveFeatureSelector (4 features total -> manageable search)")
    print("=" * 60)
    X_small, y_small = make_classification(
        n_samples=500,
        n_features=4,
        n_informative=4,
        n_redundant=0,
        random_state=rng + 1,
    )
    Xs_tr, Xs_te, ys_tr, ys_te = train_test_split(
        X_small, y_small, test_size=0.25, random_state=rng, stratify=y_small
    )
    efs = ExhaustiveFeatureSelector(
        base,
        min_features=2,
        max_features=4,
        scoring="accuracy",
        cv=3,
        n_jobs=1,
        print_progress=False,
    )
    efs.fit(Xs_tr, ys_tr)
    ex_idx = tuple(efs.best_idx_)
    base.fit(Xs_tr[:, ex_idx], ys_tr)
    acc_ex = accuracy_score(ys_te, base.predict(Xs_te[:, ex_idx]))
    print(f"  Best feature indices: {ex_idx}")
    print(f"  Best CV score (internal): {efs.best_score_:.4f}")
    print(f"  Test accuracy (subset): {acc_ex:.4f}")

    print()
    print("=" * 60)
    print("Performance comparison (test accuracy)")
    print("=" * 60)
    base.fit(X_train, y_train)
    acc_all = accuracy_score(y_test, base.predict(X_test))
    print(f"  All 8 features (baseline):     {acc_all:.4f}")
    print(f"  SFS forward (4 features):      {acc_fwd:.4f}")
    print(f"  SFS backward (4 features):     {acc_bwd:.4f}")
    print(f"  Exhaustive (small 4-D problem): {acc_ex:.4f}")


if __name__ == "__main__":
    main()
