# requires: river, scikit-learn

"""
compose.Pipeline with StandardScaler + classifier; progressive_val_score on a stream.
"""

from __future__ import annotations


def main() -> None:
    try:
        from river import compose, evaluate, metrics, preprocessing
        from river.linear_model import LogisticRegression
        from sklearn.datasets import make_classification
    except ImportError as exc:  # pragma: no cover
        print("Install river and scikit-learn to run this example:", exc)
        return

    X, y = make_classification(
        n_samples=3000,
        n_features=8,
        n_informative=6,
        random_state=55,
    )

    def to_stream():
        for xi, yi in zip(X, y, strict=True):
            x_dict = {f"f{j}": float(v) for j, v in enumerate(xi)}
            yield x_dict, int(yi)

    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        LogisticRegression(),
    )

    print("=" * 60)
    print("Pipeline: StandardScaler -> LogisticRegression")
    print("=" * 60)

    metric = metrics.Accuracy()
    score = evaluate.progressive_val_score(
        dataset=to_stream(),
        model=model,
        metric=metric,
        print_every=0,
    )
    print(f"  progressive_val_score (accuracy): {score:.4f}")
    print(f"  Metric type: {type(metric).__name__}")


if __name__ == "__main__":
    main()
