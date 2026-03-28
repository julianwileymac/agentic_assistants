# requires: scikit-learn

"""
Supervised learning basics: linear and probabilistic models on synthetic data.
"""

from __future__ import annotations


def main() -> None:
    try:
        from sklearn.datasets import make_classification, make_regression
        from sklearn.linear_model import LinearRegression, LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import GaussianNB
        from sklearn.svm import SVC
    except ImportError as exc:  # pragma: no cover
        print("Install scikit-learn to run this example:", exc)
        return

    print("=" * 60)
    print("LinearRegression (make_regression)")
    print("=" * 60)
    Xr, yr = make_regression(
        n_samples=800,
        n_features=12,
        n_informative=6,
        noise=12.0,
        random_state=42,
    )
    Xr_tr, Xr_te, yr_tr, yr_te = train_test_split(
        Xr, yr, test_size=0.25, random_state=42
    )
    lin = LinearRegression()
    lin.fit(Xr_tr, yr_tr)
    y_pred_r = lin.predict(Xr_te)
    r2 = lin.score(Xr_te, yr_te)
    print(f"  Train R^2: {lin.score(Xr_tr, yr_tr):.4f}")
    print(f"  Test R^2:  {r2:.4f}")
    print(f"  Sample preds (first 5): {y_pred_r[:5].round(3)}")

    print()
    print("=" * 60)
    print("LogisticRegression (make_classification)")
    print("=" * 60)
    Xc, yc = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=12,
        n_redundant=4,
        random_state=7,
    )
    Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
        Xc, yc, test_size=0.25, random_state=7, stratify=yc
    )
    log_reg = LogisticRegression(max_iter=500, random_state=7)
    log_reg.fit(Xc_tr, yc_tr)
    acc_lr = log_reg.score(Xc_te, yc_te)
    preds_lr = log_reg.predict(Xc_te)
    print(f"  Train accuracy: {log_reg.score(Xc_tr, yc_tr):.4f}")
    print(f"  Test accuracy:  {acc_lr:.4f}")
    print(f"  Sample preds (first 8): {preds_lr[:8]}")

    print()
    print("=" * 60)
    print("SVC (make_classification)")
    print("=" * 60)
    svc = SVC(kernel="rbf", C=1.0, gamma="scale", random_state=7)
    svc.fit(Xc_tr, yc_tr)
    acc_svc = svc.score(Xc_te, yc_te)
    preds_svc = svc.predict(Xc_te)
    print(f"  Train accuracy: {svc.score(Xc_tr, yc_tr):.4f}")
    print(f"  Test accuracy:  {acc_svc:.4f}")
    print(f"  Support vectors: {svc.n_support_.sum()}")

    print()
    print("=" * 60)
    print("GaussianNB (make_classification)")
    print("=" * 60)
    gnb = GaussianNB()
    gnb.fit(Xc_tr, yc_tr)
    acc_nb = gnb.score(Xc_te, yc_te)
    preds_nb = gnb.predict(Xc_te)
    print(f"  Train accuracy: {gnb.score(Xc_tr, yc_tr):.4f}")
    print(f"  Test accuracy:  {acc_nb:.4f}")
    print(f"  Class prior: {gnb.class_prior_.round(4)}")


if __name__ == "__main__":
    main()
