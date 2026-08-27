import pandas as pd
from pathlib import Path

def point_in_time_join(events_path: Path, as_of: str) -> pd.DataFrame:
    df = pd.read_parquet(events_path) if events_path.suffix == ".parquet" else pd.read_csv(events_path)
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    cutoff = pd.to_datetime(as_of)
    hist = df[df["event_ts"] <= cutoff]
    features = hist.groupby("user_id").agg(
        transaction_count_7d=("amount", "count"),
        avg_spend_30d=("amount", "mean"),
        failed_payment_rate=("status", lambda s: (s == "failed").mean()),
    ).reset_index()
    return features
