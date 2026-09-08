"""FastAPI serving layer for the feature store.

Exposes the online feature store and the churn model behind one API:
  - GET  /health                 -> liveness + feature contract
  - GET  /features/{user_id}     -> raw online feature lookup (no scoring)
  - GET  /predict/{user_id}      -> real-time inference (online lookup + score)
  - POST /predict                -> real-time inference from an explicit vector
  - POST /predict/batch          -> batch inference over many entity keys
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from feature_store import model as model_mod
from feature_store.online_store import FEATURE_COLUMNS, get_online_features

app = FastAPI(title="ML Feature Store Serving API", version="1.0.0")
_bundle = None


def _get_bundle():
    global _bundle
    if _bundle is None:
        _bundle = model_mod.load()
    return _bundle


class FeatureVector(BaseModel):
    transaction_count_7d: float
    avg_spend_30d: float
    failed_payment_rate: float


class BatchRequest(BaseModel):
    user_ids: List[str]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "features": FEATURE_COLUMNS}


@app.get("/features/{user_id}")
def features(user_id: str) -> dict:
    feats = get_online_features(user_id)
    if feats is None:
        raise HTTPException(status_code=404, detail="user not in online store")
    return {"user_id": user_id, "features": feats}


@app.get("/predict/{user_id}")
def predict_realtime(user_id: str) -> dict:
    """Real-time path: O(1) online lookup, then score."""
    feats = get_online_features(user_id)
    if feats is None:
        raise HTTPException(status_code=404, detail="user not in online store")
    risk = model_mod.predict_one(_get_bundle(), feats)
    return {"user_id": user_id, "churn_risk": round(risk, 4)}


@app.post("/predict")
def predict_vector(vec: FeatureVector) -> dict:
    """Real-time path from an explicit feature vector (no store lookup)."""
    risk = model_mod.predict_one(_get_bundle(), vec.model_dump())
    return {"churn_risk": round(risk, 4)}


@app.post("/predict/batch")
def predict_batch(req: BatchRequest) -> dict:
    """Batch path: score many entity keys in one call."""
    bundle = _get_bundle()
    results = []
    for uid in req.user_ids:
        feats = get_online_features(uid)
        risk: Optional[float] = None if feats is None else round(model_mod.predict_one(bundle, feats), 4)
        results.append({"user_id": uid, "churn_risk": risk})
    return {"results": results}
