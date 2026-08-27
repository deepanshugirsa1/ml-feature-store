import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

OUT = Path(__file__).parent / "raw"
OUT.mkdir(parents=True, exist_ok=True)

rows = []
base = datetime.utcnow() - timedelta(days=30)
for i in range(500):
    rows.append({
        "user_id": f"u{random.randint(1,50)}",
        "event_ts": (base + timedelta(hours=i)).isoformat(),
        "amount": round(random.uniform(5, 200), 2),
        "status": random.choice(["completed", "failed", "completed"]),
    })
pd.DataFrame(rows).to_csv(OUT / "transactions.csv", index=False)
print(f"Wrote {len(rows)} events to {OUT / 'transactions.csv'}")
