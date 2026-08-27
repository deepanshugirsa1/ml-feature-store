# Feature Store for ML-Ready Datasets

Centralized feature store ingesting events via **Kafka** and **Kinesis** simulators, materializing versioned, point-in-time correct features for ML training and serving.

> **Status: ~60% complete.** Event ingestion simulators, feature registry, point-in-time joins, and freshness monitoring run locally. Production Redshift/Snowflake deployment and automated retraining gates are planned.

## Architecture

```
Kafka / Kinesis (simulated) ──► Raw events (Parquet)
                                      │
                                      ▼
                              Feature materialization
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
            Offline store (training)            Online store (serving)
            point-in-time joins                 freshness monitors
```

## Quickstart

```bash
pip install -r requirements.txt
python data/generate_events.py
python ingestion/kafka_producer_sim.py
python pipelines/materialize_features.py
python run_demo.py
```

See [docs/ROADMAP.md](docs/ROADMAP.md).
