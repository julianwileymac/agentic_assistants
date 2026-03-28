# requires: scikit-learn

"""
Classification metrics: report, confusion matrix, ROC-AUC, precision-recall curve.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import (
            average_precision_score,
            classification_report,
            confusion_matrix,
            precision_recall_curve,
            roc_auc_score,
        )
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    X, y = make_classification(
        n_samples=1200,
        n_features=24,
        n_informative=16,
        weights=[0.65, 0.35],
        random_state=99,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=99, stratify=y
    )

    model = LogisticRegression(max_iter=500, random_state=99)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("=" * 60)
    print("classification_report")
    print("=" * 60)
    print(classification_report(y_test, y_pred, digits=4))

    print("=" * 60)
    print("confusion_matrix [[TN FP], [FN TP]] (labels 0, 1)")
    print("=" * 60)
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    tn, fp, fn, tp = cm.ravel()
    print(f"  TN={tn}  FP={fp}  FN={fn}  TP={tp}")

    print()
    print("=" * 60)
    print("roc_auc_score")
    print("=" * 60)
    roc_auc = roc_auc_score(y_test, y_prob)
    print(f"  ROC AUC: {roc_auc:.4f}")

    print()
    print("=" * 60)
    print("precision_recall_curve (summary)")
    print("=" * 60)
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    print(f"  Num thresholds+1: {len(thresholds) + 1}")
    print(f"  Precision range: [{precision.min():.4f}, {precision.max():.4f}]")
    print(f"  Recall range:    [{recall.min():.4f}, {recall.max():.4f}]")
    ap = average_precision_score(y_test, y_prob)
    print(f"  average_precision_score (AUPRC): {ap:.4f}")


if __name__ == "__main__":
    main()
