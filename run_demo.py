from pathlib import Path
from datetime import datetime
from feature_store.monitoring import check_freshness

if __name__ == "__main__":
    print(check_freshness(datetime.utcnow()))
