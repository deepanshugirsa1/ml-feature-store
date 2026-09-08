# Roadmap

## Phase 1 — done (runs locally, tested, CI)
- [x] Feature registry YAML with versioning
- [x] Kafka + Kinesis ingestion simulators
- [x] Point-in-time correct feature joins (offline store)
- [x] Online feature store (low-latency KV lookup) + training/serving contract
- [x] Churn-risk model training with AUC reporting
- [x] FastAPI serving layer — real-time, explicit-vector, and batch inference
- [x] Freshness + schema drift monitoring
- [x] Unit tests (pipeline, online store, serving) + GitHub Actions CI

## Phase 2 — managed AWS deployment
- [ ] Offline store on Redshift + Parquet in S3, built with dbt models
- [ ] Real Kafka (MSK) / Kinesis Firehose ingestion
- [ ] DynamoDB online store with TTL and versioned feature groups
- [ ] Feature-level anomaly alerts via CloudWatch

## Phase 3 — MLOps hardening
- [ ] Backfill orchestration with Airflow
- [ ] Automated regression gates before model retraining
- [ ] Feature lineage and impact analysis
- [ ] A/B feature versioning for experimentation
