"""Churn-risk model trained on point-in-time features from the offline store.

Demonstrates the training-serving contract: the exact same feature columns are
used to train the model and to score requests at serving time.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from feature_store.online_store import FEATURE_COLUMNS

MODEL_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "churn_model.joblib"
LABEL = "churned"


def train(features: pd.DataFrame, labels: pd.DataFrame, model_path: Path = MODEL_PATH) -> dict:
    df = features.merge(labels, on="user_id", how="inner")
    X = df[FEATURE_COLUMNS].fillna(0.0)
    y = df[LABEL].astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=7, stratify=y)
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_tr, y_tr)
    auc = float(roc_auc_score(y_te, clf.predict_proba(X_te)[:, 1]))
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": clf, "features": FEATURE_COLUMNS}, model_path)
    return {"auc": round(auc, 4), "n_train": int(len(X_tr)), "n_test": int(len(X_te))}


def load(model_path: Path = MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"model not found at {model_path}; run the pipeline first")
    return joblib.load(model_path)


def predict_one(bundle: dict, feats: dict) -> float:
    cols = bundle["features"]
    row = pd.DataFrame([{c: feats.get(c, 0.0) for c in cols}], columns=cols)
    return float(bundle["model"].predict_proba(row)[0, 1])
