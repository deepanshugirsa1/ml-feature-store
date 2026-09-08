import pytest
from fastapi.testclient import TestClient

from pipelines.run_pipeline import run
from serving.api import app


@pytest.fixture(scope="module")
def client():
    # Build offline+online stores and a model artifact before serving.
    run(n_users=40, n_events=1200)
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_realtime_predict(client):
    r = client.get("/predict/u1")
    assert r.status_code == 200
    body = r.json()
    assert body["user_id"] == "u1"
    assert 0.0 <= body["churn_risk"] <= 1.0


def test_predict_vector(client):
    payload = {"transaction_count_7d": 30, "avg_spend_30d": 45.0, "failed_payment_rate": 0.4}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    assert 0.0 <= r.json()["churn_risk"] <= 1.0


def test_batch_predict(client):
    r = client.post("/predict/batch", json={"user_ids": ["u1", "u2", "nope"]})
    assert r.status_code == 200
    results = r.json()["results"]
    assert len(results) == 3
    assert any(x["churn_risk"] is None for x in results)  # unknown key -> None


def test_unknown_user_404(client):
    assert client.get("/predict/ghost").status_code == 404
