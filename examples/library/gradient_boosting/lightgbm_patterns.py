# requires: lightgbm, scikit-learn, pandas, numpy

"""
LightGBM: categorical features, leaf-wise tree growth, early stopping callbacks.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from lightgbm import LGBMClassifier, early_stopping, log_evaluation
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover
        print("Install lightgbm, scikit-learn, pandas, numpy:", exc)
        return

    rng = np.random.default_rng(21)
    n = 2500
    X_num, y = make_classification(
        n_samples=n,
        n_features=12,
        n_informative=8,
        random_state=21,
    )
    cities = rng.choice(["ams", "ber", "chi", "dal"], size=n)
    bands = rng.choice(["low", "mid", "high"], size=n, p=[0.25, 0.45, 0.3])
    df = pd.DataFrame(
        {
            **{f"f{i}": X_num[:, i] for i in range(12)},
            "city": cities,
            "band": bands,
        }
    )
    for col in ("city", "band"):
        df[col] = df[col].astype("category")

    X_train, X_test, y_train, y_test = train_test_split(
        df, y, test_size=0.2, random_state=21, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=21, stratify=y_train
    )

    cat_cols = ["city", "band"]
    cat_idx = [df.columns.get_loc(c) for c in cat_cols]

    print("=" * 60)
    print("LGBMClassifier with categorical_feature (category dtypes)")
    print("=" * 60)
    # Leaf-wise growth (default for LGBM): num_leaves > max_depth in effect
    clf = LGBMClassifier(
        objective="binary",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=-1,
        min_child_samples=30,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=21,
        n_jobs=-1,
        verbose=-1,
    )
    callbacks = [
        early_stopping(stopping_rounds=40, verbose=False),
        log_evaluation(period=0),
    ]
    clf.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="binary_logloss",
        categorical_feature=cat_idx,
        callbacks=callbacks,
    )
    acc = clf.score(X_test, y_test)
    proba = clf.predict_proba(X_test.iloc[:3])[:, 1]
    print(f"  categorical_feature (column indices): {cat_idx}")
    print(f"  best_iteration: {clf.best_iteration_}")
    print(f"  Test accuracy: {acc:.4f}")
    print(f"  Sample p(class=1), first 3 rows: {proba.round(4)}")
    print(
        "  Feature importances (gain), top 5 names: "
        + ", ".join(
            f"{name}={val:.1f}"
            for name, val in sorted(
                zip(clf.feature_name_, clf.feature_importances_),
                key=lambda t: t[1],
                reverse=True,
            )[:5]
        )
    )


if __name__ == "__main__":
    main()
