"""End-to-end pipeline: generate -> materialize offline -> online -> train.

Run from the repo root:  python -m pipelines.run_pipeline
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from data.generate_events import generate
from feature_store.point_in_time import point_in_time_join
from feature_store.online_store import materialize_online
from feature_store import model as model_mod

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OFFLINE = ROOT / "data" / "features" / "offline_features.parquet"


def run(n_users: int = 50, n_events: int = 1500, as_of: str = "2099-01-01") -> dict:
    # 1) generate raw events + labels
    events, users = generate(n_users, n_events)
    RAW.mkdir(parents=True, exist_ok=True)
    events.to_csv(RAW / "transactions.csv", index=False)
    users.to_csv(RAW / "users.csv", index=False)

    # 2) offline materialization (point-in-time correct feature aggregation)
    feats = point_in_time_join(RAW / "transactions.csv", as_of=as_of)
    OFFLINE.parent.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(OFFLINE, index=False)

    # 3) online materialization (latest vector per entity for low-latency serving)
    materialize_online(feats)

    # 4) train churn model against labels
    metrics = model_mod.train(feats, users)
    return {"users": len(feats), "offline_rows": len(feats), "model": metrics}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--events", type=int, default=1500)
    args = parser.parse_args()
    result = run(args.users, args.events)
    print("pipeline complete:")
    print(f"  entities materialized : {result['users']}")
    print(f"  model AUC             : {result['model']['auc']}")
    print("  offline (Parquet) + online (KV) stores + model artifact ready for serving")


if __name__ == "__main__":
    main()
