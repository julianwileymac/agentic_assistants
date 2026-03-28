# requires: mlxtend scikit-learn

"""
Stacking and vote-based ensembles with mlxtend on synthetic classification data.

Trains a StackingClassifier and an EnsembleVoteClassifier over sklearn base estimators,
then compares blended predictions to individual model accuracy.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.base import clone
        from sklearn.datasets import make_classification
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import train_test_split
        from sklearn.svm import SVC
        from sklearn.tree import DecisionTreeClassifier
        from mlxtend.classifier import EnsembleVoteClassifier, StackingClassifier
    except ImportError as exc:  # pragma: no cover
        print("Install mlxtend and scikit-learn to run this example:", exc)
        return

    rng = 11
    X, y = make_classification(
        n_samples=900,
        n_features=16,
        n_informative=10,
        n_redundant=3,
        random_state=rng,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=rng, stratify=y
    )

    clf_lr = LogisticRegression(max_iter=1000, random_state=rng)
    clf_dt = DecisionTreeClassifier(max_depth=5, random_state=rng)
    clf_svc = SVC(kernel="rbf", probability=True, random_state=rng)

    print("=" * 60)
    print("Base estimators (individual test accuracy)")
    print("=" * 60)
    for name, est in (
        ("LogisticRegression", clf_lr),
        ("DecisionTreeClassifier", clf_dt),
        ("SVC (RBF)", clf_svc),
    ):
        est.fit(X_train, y_train)
        acc = accuracy_score(y_test, est.predict(X_test))
        print(f"  {name}: {acc:.4f}")

    print()
    print("=" * 60)
    print("StackingClassifier (meta: LogisticRegression)")
    print("=" * 60)
    stack = StackingClassifier(
        classifiers=[clone(clf_lr), clone(clf_dt), clone(clf_svc)],
        meta_classifier=LogisticRegression(max_iter=1000, random_state=rng),
        use_probas=True,
        average_probas=False,
    )
    stack.fit(X_train, y_train)
    acc_stack = accuracy_score(y_test, stack.predict(X_test))
    print(f"  Test accuracy: {acc_stack:.4f}")

    print()
    print("=" * 60)
    print("EnsembleVoteClassifier (soft voting, equal weights)")
    print("=" * 60)
    vote = EnsembleVoteClassifier(
        clfs=[clone(clf_lr), clone(clf_dt), clone(clf_svc)],
        voting="soft",
        weights=[1, 1, 1],
    )
    vote.fit(X_train, y_train)
    acc_vote = accuracy_score(y_test, vote.predict(X_test))
    print(f"  Test accuracy: {acc_vote:.4f}")

    print()
    print("=" * 60)
    print("Model blending comparison")
    print("=" * 60)
    print(f"  Stacking:   {acc_stack:.4f}")
    print(f"  Soft vote:  {acc_vote:.4f}")
    print("  (Stacking learns a meta-learner on base probabilities; voting averages them.)")


if __name__ == "__main__":
    main()
