import pandas as pd

from data.generate_events import generate
from feature_store.point_in_time import point_in_time_join
from feature_store.online_store import FEATURE_COLUMNS, materialize_online, get_online_features


def test_generate_shapes():
    events, users = generate(n_users=20, n_events=300, seed=1)
    assert set(["user_id", "event_ts", "amount", "status"]).issubset(events.columns)
    assert set(["user_id", "churned"]).issubset(users.columns)
    assert users["churned"].isin([0, 1]).all()


def test_point_in_time_features(tmp_path):
    events, _ = generate(n_users=20, n_events=300, seed=2)
    p = tmp_path / "transactions.csv"
    events.to_csv(p, index=False)
    feats = point_in_time_join(p, as_of="2099-01-01")
    for col in FEATURE_COLUMNS:
        assert col in feats.columns
    assert (feats["failed_payment_rate"].between(0, 1)).all()


def test_online_store_roundtrip(tmp_path):
    events, _ = generate(n_users=15, n_events=200, seed=3)
    p = tmp_path / "transactions.csv"
    events.to_csv(p, index=False)
    feats = point_in_time_join(p, as_of="2099-01-01")
    online = tmp_path / "online.json"
    materialize_online(feats, path=online)
    uid = str(feats["user_id"].iloc[0])
    vec = get_online_features(uid, path=online)
    assert vec is not None and set(FEATURE_COLUMNS).issubset(vec.keys())
    assert get_online_features("does-not-exist", path=online) is None
