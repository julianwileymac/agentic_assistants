# requires: river, scikit-learn

"""
Online learning: Hoeffding tree and logistic regression with learn_one / predict_one.
"""

from __future__ import annotations


def main() -> None:
    try:
        from river import linear_model
        from river.tree import HoeffdingTreeClassifier
        from sklearn.datasets import make_classification
    except ImportError as exc:  # pragma: no cover
        print("Install river and scikit-learn to run this example:", exc)
        return

    X, y = make_classification(
        n_samples=5000,
        n_features=12,
        n_informative=8,
        random_state=202,
    )

    models = {
        "HoeffdingTreeClassifier": HoeffdingTreeClassifier(),
        "LogisticRegression": linear_model.LogisticRegression(),
    }

    print("=" * 60)
    print("Streaming one sample at a time (predict_one, then learn_one)")
    print("Rolling accuracy uses the last 200 evaluated predictions (non-None only).")
    print("=" * 60)

    window = 200
    for name, model in models.items():
        correct_window: list[int] = []
        total_correct = 0
        n_eval = 0
        for xi, yi in zip(X, y, strict=True):
            x_dict = {f"f{j}": float(v) for j, v in enumerate(xi)}
            y_pred = model.predict_one(x_dict)
            if y_pred is not None:
                ok = int(y_pred) == int(yi)
                total_correct += int(ok)
                n_eval += 1
                correct_window.append(1 if ok else 0)
                if len(correct_window) > window:
                    correct_window.pop(0)
            model.learn_one(x_dict, int(yi))

        overall_acc = total_correct / n_eval if n_eval else 0.0
        rolling = sum(correct_window) / len(correct_window) if correct_window else 0.0
        print(f"  {name}")
        print(f"    Overall accuracy (where predict_one returned a class): {overall_acc:.4f}")
        print(f"    Last-{window} rolling accuracy:          {rolling:.4f}")


if __name__ == "__main__":
    main()
