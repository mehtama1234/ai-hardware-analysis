#!/usr/bin/env python3
"""Verify autotuning database records and selector behavior."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTOTUNE = ROOT / "autotune-db"
DB = AUTOTUNE / "autotune-db.json"
SITE_PAGE = ROOT / "site" / "autotune-db.html"
REQUIRED_FAMILIES = {"memory", "reduction", "normalization", "matmul", "fusion", "custom-op"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    if not DB.exists():
        subprocess.run([sys.executable, "scripts/build_autotune_db.py"], cwd=ROOT, check=True)
    database = load_json(DB)
    records = database.get("records", [])
    families = set(database.get("families", []))
    require(database.get("record_count") == len(records), "autotune record count mismatch")
    require(len(records) >= 18, "expected kernel benchmark and custom-op records")
    require(REQUIRED_FAMILIES.issubset(families), f"missing autotune families: {sorted(REQUIRED_FAMILIES - families)}")
    for record in records:
        require(record.get("candidate_count", 0) >= 3, f"{record.get('id')} lacks candidate configs")
        require(len(record.get("candidates", [])) == record.get("candidate_count"), f"{record.get('id')} candidate count mismatch")
        selected = record.get("selected", {})
        require(selected in record.get("candidates", []), f"{record.get('id')} selected config not in candidates")
        require(record.get("selection_status") == "proposed_not_measured", f"{record.get('id')} selection status overclaims execution")
        require(selected.get("evidence_kind") == "analytical", f"{record.get('id')} candidate evidence kind missing")
        require(selected.get("measured") is False, f"{record.get('id')} analytical candidate marked measured")
        require(selected.get("estimated_speedup_vs_measured", 0) >= 1.0, f"{record.get('id')} selected config regresses")
        require(record.get("promotion_targets"), f"{record.get('id')} missing promotion targets")
        require(record.get("measured_seconds", 0) >= 0, f"{record.get('id')} missing measured seconds")
    if SITE_PAGE.exists():
        page = SITE_PAGE.read_text(encoding="utf-8")
        require("GPUMODE autotuning database" in page, "autotune site page missing title")
        require("modeled speedup" in page, "autotune site page missing modeled status column")
    facts = {
        "records": database["record_count"],
        "families": sorted(families),
        "source_reports": database.get("source_reports", []),
    }
    print(json.dumps({"facts": facts, "failures": []}, indent=2))
    print("GPUMODE autotune database verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
