import yaml
from pathlib import Path
from datetime import datetime, timedelta

REG = Path(__file__).resolve().parent / "registry.yaml"

def check_freshness(last_updated: datetime) -> dict:
    features = yaml.safe_load(REG.read_text())["features"]
    alerts = []
    for f in features:
        sla = timedelta(hours=f["freshness_sla_hours"])
        if datetime.utcnow() - last_updated > sla:
            alerts.append({"feature": f["name"], "status": "STALE"})
    return {"ok": len(alerts) == 0, "alerts": alerts}
