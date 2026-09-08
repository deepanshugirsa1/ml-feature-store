"""Low-latency online feature store for real-time serving.

The offline store (Parquet, produced by the materialization pipeline) is the
source of truth for training. This module snapshots the latest feature row per
entity into a key-value store (JSON here; DynamoDB/Redis in the roadmap) so the
serving API can do O(1) lookups by ``user_id``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = ["transaction_count_7d", "avg_spend_30d", "failed_payment_rate"]

ROOT = Path(__file__).resolve().parents[1] / "data"
ONLINE_PATH = ROOT / "online" / "online_features.json"


def materialize_online(features: pd.DataFrame, path: Path = ONLINE_PATH) -> Path:
    """Write the latest feature vector per entity to the online KV store."""
    path.parent.mkdir(parents=True, exist_ok=True)
    table = features.set_index("user_id")[FEATURE_COLUMNS].round(6)
    path.write_text(json.dumps({str(k): v for k, v in table.to_dict("index").items()}))
    return path


def get_online_features(user_id: str, path: Path = ONLINE_PATH) -> dict | None:
    """O(1) lookup of the current feature vector for one entity."""
    if not path.exists():
        return None
    table = json.loads(path.read_text())
    return table.get(str(user_id))
