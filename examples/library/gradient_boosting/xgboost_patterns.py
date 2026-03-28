# requires: xgboost, scikit-learn

"""
XGBoost sklearn API: classification/regression, early stopping, feature importance.
"""

from __future__ import annotations


def _fit_classifier_with_early_stopping(clf, X_train, y_train, X_val, y_val) -> None:
    """Support both legacy ``early_stopping_rounds`` and callback-based XGBoost."""
    try:
        clf.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=30,
            verbose=False,
        )
    except TypeError:
        from xgboost.callback import EarlyStopping

        clf.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[EarlyStopping(rounds=30, save_best=True)],
            verbose=False,
        )


def _fit_regressor_with_early_stopping(reg, X_train, y_train, X_val, y_val) -> None:
    try:
        reg.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=30,
            verbose=False,
        )
    except TypeError:
        from xgboost.callback import EarlyStopping

        reg.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[EarlyStopping(rounds=30, save_best=True)],
            verbose=False,
        )


def main() -> None:
    try:
        from sklearn.datasets import make_classification, make_regression
        from sklearn.model_selection import train_test_split
        from xgboost import XGBClassifier, XGBRegressor
    except ImportError as exc:  # pragma: no cover
        print("Install xgboost and scikit-learn to run this example:", exc)
        return

    print("=" * 60)
    print("XGBClassifier + eval_set / early stopping")
    print("=" * 60)
    Xc, yc = make_classification(
        n_samples=2000,
        n_features=24,
        n_informative=14,
        random_state=3,
    )
    Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
        Xc, yc, test_size=0.2, random_state=3, stratify=yc
    )
    Xc_tr, Xc_val, yc_tr, yc_val = train_test_split(
        Xc_tr, yc_tr, test_size=0.15, random_state=3, stratify=yc_tr
    )
    clf = XGBClassifier(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.85,
        random_state=3,
        n_jobs=-1,
    )
    _fit_classifier_with_early_stopping(clf, Xc_tr, yc_tr, Xc_val, yc_val)
    acc = clf.score(Xc_te, yc_te)
    preds = clf.predict(Xc_te[:5])
    print(f"  Test accuracy: {acc:.4f}")
    print(f"  Sample predictions (first 5): {preds}")
    imp = clf.feature_importances_
    top = sorted(enumerate(imp), key=lambda t: t[1], reverse=True)[:5]
    print("  Top-5 feature_importances_ (idx, importance):")
    for idx, val in top:
        print(f"    {idx:2d}  {val:.5f}")

    print()
    print("=" * 60)
    print("XGBRegressor + eval_set / early stopping")
    print("=" * 60)
    Xr, yr = make_regression(
        n_samples=1500,
        n_features=18,
        n_informative=10,
        noise=8.0,
        random_state=5,
    )
    Xr_tr, Xr_te, yr_tr, yr_te = train_test_split(
        Xr, yr, test_size=0.2, random_state=5
    )
    Xr_tr, Xr_val, yr_tr, yr_val = train_test_split(
        Xr_tr, yr_tr, test_size=0.15, random_state=5
    )
    reg = XGBRegressor(
        n_estimators=600,
        max_depth=3,
        learning_rate=0.06,
        subsample=0.9,
        random_state=5,
        n_jobs=-1,
    )
    _fit_regressor_with_early_stopping(reg, Xr_tr, yr_tr, Xr_val, yr_val)
    r2 = reg.score(Xr_te, yr_te)
    yhat = reg.predict(Xr_te[:5])
    print(f"  Test R^2: {r2:.4f}")
    print(f"  Sample predictions (first 5): {yhat.round(3)}")
    imp_r = reg.feature_importances_
    top_r = sorted(enumerate(imp_r), key=lambda t: t[1], reverse=True)[:5]
    print("  Top-5 feature_importances_ (idx, importance):")
    for idx, val in top_r:
        print(f"    {idx:2d}  {val:.5f}")


if __name__ == "__main__":
    main()
