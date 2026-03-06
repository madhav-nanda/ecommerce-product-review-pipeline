"""DQ report writer."""
from pathlib import Path
import json


def write_dq_report(report: dict, run_id: str) -> Path:
    out = Path("data/reports")
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"dq_{run_id}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path
