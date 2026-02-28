import json
import sys
from datetime import datetime
import random

STATUS_FILE = "status.json"

source_id = None
if len(sys.argv) > 1:
    source_id = sys.argv[1]

# Dummy example data
sample_sources = {
    "1001": {
        "overall_status": random.choice(["Changed", "No Change"]),
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "urls": [
            {"url": "https://example.com/page1", "status": "No Change"},
            {"url": "https://example.com/page2", "status": random.choice(["Changed", "No Change"])}
        ]
    },
    "1002": {
        "overall_status": random.choice(["Changed", "No Change"]),
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "urls": [
            {"url": "https://example2.com/page1", "status": "No Change"}
        ]
    }
}

if source_id:
    if source_id in sample_sources:
        sample_sources = {source_id: sample_sources[source_id]}

with open(STATUS_FILE, "w", encoding="utf-8") as f:
    json.dump(sample_sources, f, indent=4)

print("Monitor script executed successfully")