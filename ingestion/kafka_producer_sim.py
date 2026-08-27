"""Simulates Kafka event stream to local parquet partition."""
import pandas as pd
from pathlib import Path
from datetime import datetime

SRC = Path(__file__).resolve().parents[1] / "data" / "raw" / "transactions.csv"
OUT = Path(__file__).resolve().parents[1] / "data" / "kafka_stream"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(SRC)
    part = OUT / f"dt={datetime.utcnow():%Y-%m-%d}" / "events.parquet"
    part.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(part, index=False)
    print(f"Kafka sim wrote {len(df)} rows to {part}")

if __name__ == "__main__":
    main()
