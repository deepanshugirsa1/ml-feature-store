from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from feature_store.point_in_time import point_in_time_join

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "transactions.csv"
OUT = Path(__file__).resolve().parents[1] / "data" / "features"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    feats = point_in_time_join(RAW, as_of="2099-01-01")
    out = OUT / "offline_features.parquet"
    feats.to_parquet(out, index=False)
    print(f"Materialized {len(feats)} user feature rows to {out}")

if __name__ == "__main__":
    main()
