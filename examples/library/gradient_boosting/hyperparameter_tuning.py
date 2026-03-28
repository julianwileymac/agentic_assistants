# requires: xgboost lightgbm catboost

"""
Optuna-driven hyperparameter search for XGBoost, LightGBM, and CatBoost with
stratified CV, early stopping inside trials, and final retrain on full data.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import StratifiedKFold
    except ImportError as exc:  # pragma: no cover
        print("Install numpy and scikit-learn:", exc)
        return

    try:
        import optuna
    except ImportError:
        print("Install optuna to run this example: pip install optuna")
        return

    try:
        from catboost import CatBoostClassifier
        from lightgbm import LGBMClassifier, early_stopping, log_evaluation
        from xgboost import XGBClassifier
    except ImportError as exc:  # pragma: no cover
        print("Install xgboost, lightgbm, and catboost:", exc)
        return

    rng = 17
    X, y = make_classification(
        n_samples=2400,
        n_features=18,
        n_informative=11,
        random_state=rng,
    )

    print("=" * 60)
    print("Optuna + XGBoost (3-fold CV, early stopping per fold)")
    print("=" * 60)

    def xgb_objective(trial: optuna.Trial) -> float:
        params = {
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.2, log=True),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 8),
            "n_estimators": 600,
            "random_state": rng,
            "n_jobs": -1,
            "eval_metric": "logloss",
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=rng)
        scores: list[float] = []
        for tr_idx, va_idx in skf.split(X, y):
            X_tr, X_va = X[tr_idx], X[va_idx]
            y_tr, y_va = y[tr_idx], y[va_idx]
            clf = XGBClassifier(**params)
            try:
                clf.fit(
                    X_tr,
                    y_tr,
                    eval_set=[(X_va, y_va)],
                    early_stopping_rounds=40,
                    verbose=False,
                )
            except TypeError:
                from xgboost.callback import EarlyStopping

                clf.fit(
                    X_tr,
                    y_tr,
                    eval_set=[(X_va, y_va)],
                    callbacks=[EarlyStopping(rounds=40, save_best=True)],
                    verbose=False,
                )
            pred = clf.predict(X_va)
            scores.append(accuracy_score(y_va, pred))
        return float(np.mean(scores))

    study_xgb = optuna.create_study(direction="maximize", study_name="xgb")
    study_xgb.optimize(xgb_objective, n_trials=12, show_progress_bar=False)
    best_xgb = study_xgb.best_trial.params
    best_xgb["n_estimators"] = 800
    best_xgb["random_state"] = rng
    best_xgb["n_jobs"] = -1
    best_xgb["eval_metric"] = "logloss"
    final_xgb = XGBClassifier(**best_xgb)
    final_xgb.fit(X, y, verbose=False)
    print(f"  Best trial value (mean CV acc): {study_xgb.best_value:.4f}")
    print(f"  Best params (key subset): { {k: best_xgb[k] for k in list(best_xgb)[:5]} }")
    print(f"  Retrained on full data — sample preds: {final_xgb.predict(X[:3])}")

    print()
    print("=" * 60)
    print("Optuna + LightGBM (CV + early_stopping callbacks)")
    print("=" * 60)

    def lgb_objective(trial: optuna.Trial) -> float:
        params = {
            "num_leaves": trial.suggest_int("num_leaves", 31, 127),
            "learning_rate": trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
            "subsample": trial.suggest_float("subsample", 0.7, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.7, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 10, 80),
            "n_estimators": 700,
            "random_state": rng,
            "n_jobs": -1,
            "verbose": -1,
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=rng)
        scores: list[float] = []
        for tr_idx, va_idx in skf.split(X, y):
            X_tr, X_va = X[tr_idx], X[va_idx]
            y_tr, y_va = y[tr_idx], y[va_idx]
            clf = LGBMClassifier(**params)
            clf.fit(
                X_tr,
                y_tr,
                eval_set=[(X_va, y_va)],
                eval_metric="binary_logloss",
                callbacks=[
                    early_stopping(stopping_rounds=45, verbose=False),
                    log_evaluation(period=0),
                ],
            )
            pred = clf.predict(X_va)
            scores.append(accuracy_score(y_va, pred))
        return float(np.mean(scores))

    study_lgb = optuna.create_study(direction="maximize", study_name="lgb")
    study_lgb.optimize(lgb_objective, n_trials=12, show_progress_bar=False)
    best_lgb = study_lgb.best_trial.params
    best_lgb["n_estimators"] = 900
    best_lgb["random_state"] = rng
    best_lgb["n_jobs"] = -1
    best_lgb["verbose"] = -1
    final_lgb = LGBMClassifier(**best_lgb)
    final_lgb.fit(X, y)
    print(f"  Best trial value (mean CV acc): {study_lgb.best_value:.4f}")
    print(f"  Retrained on full data — sample preds: {final_lgb.predict(X[:3])}")

    print()
    print("=" * 60)
    print("Optuna + CatBoost (CV + early stopping on eval set)")
    print("=" * 60)

    def cat_objective(trial: optuna.Trial) -> float:
        depth = trial.suggest_int("depth", 4, 8)
        lr = trial.suggest_float("learning_rate", 0.03, 0.2, log=True)
        l2 = trial.suggest_float("l2_leaf_reg", 1.0, 10.0)
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=rng)
        scores: list[float] = []
        for tr_idx, va_idx in skf.split(X, y):
            X_tr, X_va = X[tr_idx], X[va_idx]
            y_tr, y_va = y[tr_idx], y[va_idx]
            model = CatBoostClassifier(
                iterations=500,
                depth=depth,
                learning_rate=lr,
                l2_leaf_reg=l2,
                loss_function="Logloss",
                random_seed=rng,
                verbose=False,
                early_stopping_rounds=40,
            )
            model.fit(X_tr, y_tr, eval_set=(X_va, y_va))
            pred = model.predict(X_va)
            scores.append(accuracy_score(y_va, pred.astype(np.int64).ravel()))
        return float(np.mean(scores))

    study_cat = optuna.create_study(direction="maximize", study_name="cat")
    study_cat.optimize(cat_objective, n_trials=10, show_progress_bar=False)
    bp = study_cat.best_trial.params
    final_cat = CatBoostClassifier(
        iterations=800,
        depth=bp["depth"],
        learning_rate=bp["learning_rate"],
        l2_leaf_reg=bp["l2_leaf_reg"],
        loss_function="Logloss",
        random_seed=rng,
        verbose=False,
    )
    final_cat.fit(X, y)
    print(f"  Best trial value (mean CV acc): {study_cat.best_value:.4f}")
    print(f"  Retrained on full data — sample preds: {final_cat.predict(X[:3]).ravel()}")


if __name__ == "__main__":
    main()
