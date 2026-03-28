# requires: scikit-learn, pandas

"""
Pipelines, mixed-type ColumnTransformer, cross_val_score, and GridSearchCV.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from sklearn.compose import ColumnTransformer
        from sklearn.datasets import make_classification
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn and pandas to run this example:", exc)
        return

    print("=" * 60)
    print("Pipeline: StandardScaler + LogisticRegression (numeric only)")
    print("=" * 60)
    X_simple, y_simple = make_classification(
        n_samples=600,
        n_features=12,
        random_state=42,
    )
    Xs_tr, Xs_te, ys_tr, ys_te = train_test_split(
        X_simple, y_simple, test_size=0.25, random_state=42, stratify=y_simple
    )
    simple_pipe = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500, random_state=42)),
        ]
    )
    simple_pipe.fit(Xs_tr, ys_tr)
    print(f"  Hold-out accuracy: {simple_pipe.score(Xs_te, ys_te):.4f}")

    rng = np.random.default_rng(42)
    n = 800
    df = pd.DataFrame(
        {
            "income": rng.normal(50_000, 12_000, n).clip(15_000, 120_000),
            "age": rng.integers(22, 70, size=n),
            "score": rng.normal(0.5, 0.15, n).clip(0, 1),
            "region": rng.choice(["north", "south", "east", "west"], size=n),
            "tier": rng.choice(["basic", "plus", "pro"], size=n, p=[0.5, 0.35, 0.15]),
        }
    )
    # Synthetic binary label: higher score + certain regions tilt positive
    logit = (
        (df["score"] - 0.5) * 4.0
        + (df["age"] - 45) / 40.0
        + (df["income"] - 50_000) / 25_000
        + (df["region"].map({"north": 0.2, "south": -0.1, "east": 0.0, "west": 0.15}))
        + rng.normal(0, 0.35, n)
    )
    y = (logit > 0).astype(int)

    numeric_features = ["income", "age", "score"]
    categorical_features = ["region", "tier"]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ]
    )

    clf_pipe = Pipeline(
        steps=[
            ("prep", preprocessor),
            ("clf", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        df, y, test_size=0.25, random_state=42, stratify=y
    )

    print("=" * 60)
    print("Pipeline: StandardScaler (numeric) + OHE (cat) + LogisticRegression")
    print("=" * 60)
    clf_pipe.fit(X_train, y_train)
    test_acc = clf_pipe.score(X_test, y_test)
    print(f"  Hold-out accuracy: {test_acc:.4f}")

    print()
    print("=" * 60)
    print("cross_val_score (5-fold, accuracy)")
    print("=" * 60)
    cv_scores = cross_val_score(clf_pipe, df, y, cv=5, scoring="accuracy")
    print(f"  Fold scores: {cv_scores.round(4)}")
    print(f"  Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    print()
    print("=" * 60)
    print("GridSearchCV over clf__C and clf__solver")
    print("=" * 60)
    param_grid = {
        "clf__C": [0.1, 1.0, 10.0],
        "clf__solver": ["lbfgs", "saga"],
    }
    grid = GridSearchCV(
        clf_pipe,
        param_grid=param_grid,
        cv=4,
        scoring="accuracy",
        n_jobs=1,
    )
    grid.fit(df, y)
    print(f"  Best CV score: {grid.best_score_:.4f}")
    print(f"  Best params: {grid.best_params_}")
    print(f"  Refit test accuracy (same split): {grid.score(X_test, y_test):.4f}")


if __name__ == "__main__":
    main()
