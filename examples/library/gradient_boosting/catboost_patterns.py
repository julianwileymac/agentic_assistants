# requires: catboost, scikit-learn, pandas, numpy

"""
CatBoost: cat_features on a DataFrame and Pool-based training/evaluation.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        import pandas as pd
        from catboost import CatBoostClassifier, Pool
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover
        print("Install catboost, scikit-learn, pandas, numpy:", exc)
        return

    rng = np.random.default_rng(33)
    n = 2200
    X_num, y = make_classification(
        n_samples=n,
        n_features=10,
        n_informative=7,
        random_state=33,
    )
    dept = rng.choice(["sales", "eng", "ops", "hq"], size=n)
    channel = rng.choice(["web", "store", "partner"], size=n, p=[0.5, 0.35, 0.15])
    df = pd.DataFrame(
        {
            **{f"n{i}": X_num[:, i] for i in range(10)},
            "dept": dept,
            "channel": channel,
        }
    )

    cat_features = ["dept", "channel"]
    X_train, X_test, y_train, y_test = train_test_split(
        df, y, test_size=0.2, random_state=33, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=33, stratify=y_train
    )

    print("=" * 60)
    print("CatBoostClassifier with cat_features + Pool API")
    print("=" * 60)

    train_pool = Pool(data=X_train, label=y_train, cat_features=cat_features)
    val_pool = Pool(data=X_val, label=y_val, cat_features=cat_features)

    model = CatBoostClassifier(
        depth=5,
        learning_rate=0.06,
        iterations=400,
        loss_function="Logloss",
        eval_metric="AUC",
        random_seed=33,
        verbose=False,
        early_stopping_rounds=35,
    )
    model.fit(train_pool, eval_set=val_pool, use_best_model=True)

    acc = model.score(X_test, y_test)
    preds = model.predict(X_test.iloc[:5], prediction_type="Class").ravel()
    proba = model.predict_proba(X_test.iloc[:5])[:, 1]

    print(f"  cat_features: {cat_features}")
    print(f"  best_iteration_: {model.get_best_iteration()}")
    print(f"  Test accuracy (hold-out rows): {acc:.4f}")
    print(f"  Sample class preds (first 5): {preds.astype(int)}")
    print(f"  Sample p(class=1) (first 5): {np.round(proba, 4)}")

    names = model.feature_names_
    scores = model.get_feature_importance(train_pool, type="PredictionValuesChange")
    ranking = sorted(zip(names, scores), key=lambda t: t[1], reverse=True)[:6]
    print("  Top feature importances (PredictionValuesChange):")
    for name, score in ranking:
        print(f"    {name:12s}  {score:.4f}")


if __name__ == "__main__":
    main()
