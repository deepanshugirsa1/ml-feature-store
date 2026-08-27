"""Simulates Kinesis shard output to local parquet."""
import shutil
from pathlib import Path

KAFKA = Path(__file__).resolve().parents[1] / "data" / "kafka_stream"
KINESIS = Path(__file__).resolve().parents[1] / "data" / "kinesis_stream"
KINESIS.mkdir(parents=True, exist_ok=True)

def main():
    for f in KAFKA.rglob("*.parquet"):
        dest = KINESIS / f.name
        shutil.copy(f, dest)
        print(f"Kinesis sim copied {f.name}")

if __name__ == "__main__":
    main()
