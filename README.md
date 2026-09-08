# Feature Store for ML-Ready Datasets

A centralized **feature store** that ingests events via **Kafka/Kinesis** simulators,
materializes **versioned, point-in-time-correct** features into an **offline store**
(training) and an **online store** (serving), trains a **churn-risk model**, and
**productionizes it behind a FastAPI serving layer** with both **batch and real-time
inference**.

> **Status: end-to-end and runnable.** `generate → ingest → materialize (offline +
> online) → train → serve` all run locally with tests and CI. Managed AWS deployment
> (Redshift/Glue/Kinesis, DynamoDB online store, Airflow orchestration) is the
> documented next step — see [docs/ROADMAP.md](docs/ROADMAP.md).

## Architecture

```
   Kafka / Kinesis (simulated) ──► Raw events (CSV/Parquet)
                                        │
                             point-in-time feature build
                                        │
                 ┌──────────────────────┴───────────────────────┐
                 ▼                                               ▼
        Offline store (Parquet)                        Online store (KV / JSON)
        point-in-time joins  ──► model training        latest vector per entity
        freshness monitors        (LogReg, AUC)                 │
                                        │                       ▼
                                        └────────► FastAPI serving layer
                                                     ├─ GET  /features/{id}   (lookup)
                                                     ├─ GET  /predict/{id}    (real-time)
                                                     ├─ POST /predict         (vector)
                                                     └─ POST /predict/batch   (batch)
```

The **same feature columns** are used for training and serving — the training/serving
contract is enforced in `feature_store/online_store.py::FEATURE_COLUMNS`.

## Quickstart

```bash
pip install -r requirements.txt

# build offline + online stores and train the model, then exercise the API
python run_demo.py

# or step by step
python -m pipelines.run_pipeline           # generate -> materialize -> train
uvicorn serving.api:app --reload           # serve on http://127.0.0.1:8000
pytest -q                                  # run the test suite
```

Example serving calls:

```bash
curl localhost:8000/health
curl localhost:8000/predict/u1                                  # real-time (online lookup + score)
curl -X POST localhost:8000/predict/batch \
  -H "content-type: application/json" \
  -d '{"user_ids": ["u1","u2","u3"]}'                           # batch inference
```

## Layout

| Path | Purpose |
|------|---------|
| `data/generate_events.py` | Synthetic event stream + churn labels (privacy-safe) |
| `ingestion/` | Kafka + Kinesis stream simulators |
| `feature_store/point_in_time.py` | Point-in-time-correct feature joins (offline) |
| `feature_store/online_store.py` | Low-latency online KV store + serving contract |
| `feature_store/model.py` | Churn model train / load / score |
| `feature_store/monitoring.py` | Feature freshness / SLA checks |
| `pipelines/run_pipeline.py` | End-to-end orchestration |
| `serving/api.py` | FastAPI: real-time, vector, and batch inference |
| `tests/` | Pipeline, online-store, and serving tests |

## Stack

Python, pandas, PyArrow, scikit-learn, FastAPI, Uvicorn, Pydantic, PyYAML.
Roadmap: AWS Redshift/Glue/Kinesis, DynamoDB, Airflow, CloudWatch.

## License

MIT
