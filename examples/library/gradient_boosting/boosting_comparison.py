# requires: scikit-learn; optional: xgboost, lightgbm, catboost

"""
Train XGBoost, LightGBM, and CatBoost on the same synthetic dataset; time and compare accuracy.
"""

from __future__ import annotations

import time
from typing import Callable


def main() -> None:
    try:
        from sklearn.datasets import make_classification
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    X, y = make_classification(
        n_samples=4000,
        n_features=20,
        n_informative=12,
        random_state=101,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=101, stratify=y
    )

    results: list[tuple[str, float | None, float | None, str]] = []

    def bench(name: str, run: Callable[[], float]) -> None:
        t0 = time.perf_counter()
        try:
            acc = run()
            elapsed = time.perf_counter() - t0
            results.append((name, elapsed, acc, "ok"))
        except ImportError:
            results.append((name, None, None, "missing package"))
        except Exception as exc:  # pragma: no cover
            results.append((name, None, None, f"error: {exc}"))

    def run_xgb() -> float:
        from xgboost import XGBClassifier

        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.9,
            random_state=101,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        return float(model.score(X_test, y_test))

    def run_lgb() -> float:
        from lightgbm import LGBMClassifier

        model = LGBMClassifier(
            n_estimators=250,
            learning_rate=0.06,
            num_leaves=48,
            random_state=101,
            n_jobs=-1,
            verbose=-1,
        )
        model.fit(X_train, y_train)
        return float(model.score(X_test, y_test))

    def run_cat() -> float:
        from catboost import CatBoostClassifier

        model = CatBoostClassifier(
            iterations=250,
            depth=5,
            learning_rate=0.08,
            random_seed=101,
            verbose=False,
        )
        model.fit(X_train, y_train)
        return float(model.score(X_test, y_test))

    bench("XGBoost", run_xgb)
    bench("LightGBM", run_lgb)
    bench("CatBoost", run_cat)

    print("=" * 72)
    print("Boosting comparison (same synthetic classification data)")
    print("=" * 72)
    print(f"{'Library':<12} {'Time (s)':>12} {'Accuracy':>12} {'Status':<20}")
    print("-" * 72)
    for name, elapsed, acc, status in results:
        if elapsed is None:
            t_str = "         n/a"
            a_str = "         n/a"
        else:
            t_str = f"{elapsed:12.4f}"
            a_str = f"{acc:12.4f}" if acc is not None else "         n/a"
        print(f"{name:<12} {t_str:>12} {a_str:>12} {status:<20}")
    print("-" * 72)


if __name__ == "__main__":
    main()
