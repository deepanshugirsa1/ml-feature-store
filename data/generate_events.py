"""Synthetic event + label generator for the feature store.

Emits two privacy-safe, fully synthetic tables:
  - transactions.csv : raw per-event stream (ingested via the Kafka/Kinesis sims)
  - users.csv        : per-user churn label used for supervised training

No real data is used.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import numpy as np
import pandas as pd

OUT = Path(__file__).parent / "raw"


def generate(n_users: int = 50, n_events: int = 1500, seed: int = 7):
    rng = np.random.default_rng(seed)
    base = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)

    # ---- raw event stream ----
    user_ids = [f"u{i}" for i in range(1, n_users + 1)]
    # per-user latent "health": drives spend, failure rate, and churn
    health = {u: rng.uniform(0.1, 0.95) for u in user_ids}

    rows = []
    for i in range(n_events):
        u = rng.choice(user_ids)
        h = health[u]
        amount = round(float(rng.gamma(2.0, 30.0 * h + 5.0)), 2)
        failed = rng.random() > (0.6 + 0.35 * h)  # unhealthy users fail more
        rows.append({
            "user_id": u,
            "event_ts": (base + timedelta(minutes=int(i * (43200 / n_events)))).isoformat(),
            "amount": amount,
            "status": "failed" if failed else "completed",
        })
    events = pd.DataFrame(rows)

    # ---- per-user churn label (from latent health + realized signals) ----
    agg = events.assign(is_failed=(events["status"] == "failed").astype(int)).groupby("user_id").agg(
        n=("amount", "size"),
        avg_amt=("amount", "mean"),
        fail_rate=("is_failed", "mean"),
    )
    logit = (
        1.5
        - 3.0 * agg.index.map(health).astype(float)
        + 2.0 * agg["fail_rate"]
        - 0.01 * agg["avg_amt"]
        - 0.05 * agg["n"]
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    churned = (rng.random(len(agg)) < prob).astype(int)
    users = pd.DataFrame({"user_id": agg.index, "churned": churned}).reset_index(drop=True)

    return events, users


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--events", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    events, users = generate(args.users, args.events, args.seed)
    events.to_csv(OUT / "transactions.csv", index=False)
    users.to_csv(OUT / "users.csv", index=False)
    print(f"Wrote {len(events)} events -> {OUT / 'transactions.csv'}")
    print(f"Wrote {len(users)} user labels -> {OUT / 'users.csv'} (churn rate {users['churned'].mean():.1%})")


if __name__ == "__main__":
    main()
