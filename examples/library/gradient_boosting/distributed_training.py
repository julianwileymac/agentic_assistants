# requires: xgboost lightgbm catboost

"""
Distributed training patterns: XGBoost + Dask (optional), LightGBM distributed
learners, and CatBoost multi-GPU configuration. Uses synthetic tabular data only.
"""

from __future__ import annotations


def main() -> None:
    try:
        import numpy as np
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn (and numpy) for synthetic data:", exc)
        return

    X, y = make_classification(
        n_samples=4000,
        n_features=20,
        n_informative=12,
        random_state=9,
    )
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=9, stratify=y
    )

    print("=" * 60)
    print("XGBoost + Dask: setup pattern and DaskDMatrix concepts")
    print("=" * 60)
    print(
        "  DaskDMatrix shards partitions across workers; labels must align row-wise.\n"
        "  Typical flow: dask.array / dask.dataframe -> DaskDMatrix -> xgboost.train\n"
        "  with a live dask.distributed.Client."
    )
    try:
        import dask.array as da
        from dask.distributed import Client

        import xgboost as xgb
        from xgboost.dask import DaskDMatrix, train as dask_train
    except ImportError as exc:
        print("  (Skipped) Install dask, distributed, and xgboost for a live demo:", exc)
    else:
        # Small local cluster for illustration; production uses a real scheduler address.
        client = Client(processes=False, silence_logs=50)
        try:
            row_chunk = max(1, len(X_tr) // 4)
            X_da = da.from_array(X_tr, chunks=(row_chunk, X_tr.shape[1]))
            y_da = da.from_array(y_tr, chunks=(row_chunk,))
            dmatrix = DaskDMatrix(client, X_da, y_da)
            params = {
                "objective": "binary:logistic",
                "eval_metric": "logloss",
                "max_depth": 4,
                "eta": 0.15,
                "tree_method": "hist",
            }
            output = dask_train(
                client,
                params,
                dmatrix,
                num_boost_round=40,
            )
            booster = output["booster"]
            d_te = xgb.DMatrix(X_te)
            proba = booster.predict(d_te)
            acc = float(np.mean((proba > 0.5).astype(np.int64) == y_te))
            print(f"  Local Client demo - hold-out accuracy (~{acc:.4f})")
        finally:
            client.close()

    print()
    print("=" * 60)
    print("LightGBM: distributed / collaborative tree_learner settings")
    print("=" * 60)
    try:
        from lightgbm import LGBMClassifier
    except ImportError as exc:  # pragma: no cover
        print("Install lightgbm (optional section):", exc)
    else:
        # data_parallel / feature_parallel require multi-process orchestration in practice.
        lgbm_dist_params = {
            "tree_learner": "data",
            "num_leaves": 63,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "n_jobs": -1,
            "verbose": -1,
        }
        print("  Example params for horizontal(data) partitioning across workers:")
        for k, v in lgbm_dist_params.items():
            print(f"    {k}: {v!r}")
        clf_lgb = LGBMClassifier(**lgbm_dist_params)
        clf_lgb.fit(X_tr, y_tr)
        print(f"  Local single-process sanity check - test acc: {clf_lgb.score(X_te, y_te):.4f}")

    print()
    print("=" * 60)
    print("CatBoost: multi-GPU task_type / devices pattern")
    print("=" * 60)
    try:
        from catboost import CatBoostClassifier
    except ImportError as exc:  # pragma: no cover
        print("Install catboost (optional section):", exc)
    else:
        print(
            "  Multi-GPU (when available): task_type='GPU', devices='0:1' (or '0-3').\n"
            "  Falls back to CPU below if no GPU."
        )
        try:
            from catboost.utils import get_gpu_device_count

            gpu_ok = get_gpu_device_count() > 0
        except Exception:
            gpu_ok = False

        cat_params = {
            "iterations": 250,
            "depth": 5,
            "learning_rate": 0.06,
            "loss_function": "Logloss",
            "verbose": False,
            "random_seed": 9,
        }
        if gpu_ok:
            cat_params["task_type"] = "GPU"
            cat_params["devices"] = "0"
        cbc = CatBoostClassifier(**cat_params)
        cbc.fit(X_tr, y_tr, eval_set=(X_te, y_te), early_stopping_rounds=30)
        print(
            f"  task_type={cat_params.get('task_type', 'CPU')} - test acc: "
            f"{cbc.score(X_te, y_te):.4f}"
        )


if __name__ == "__main__":
    main()
