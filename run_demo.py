"""End-to-end demo: build the stores + model, then exercise the serving paths.

    python run_demo.py
"""
from fastapi.testclient import TestClient

from pipelines.run_pipeline import run
from serving.api import app


def main() -> None:
    result = run()
    print(f"[pipeline] entities={result['users']}  model AUC={result['model']['auc']}")

    client = TestClient(app)
    print("[health ]", client.get("/health").json())
    print("[online ]", client.get("/features/u1").json())
    print("[real-time]", client.get("/predict/u1").json())
    print("[batch  ]", client.post("/predict/batch", json={"user_ids": ["u1", "u2", "u3"]}).json())


if __name__ == "__main__":
    main()
