"""Independently validate the specification-grounded assertion matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

SUBREPO = Path(__file__).resolve().parent.parent / "analog-digital-chip-design-eda"
sys.path.insert(0, str(SUBREPO))
from scripts.run_four_workstream_assertion_matrix import verify_matrix_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    result = verify_matrix_report(args.report)
    payload = {"schema_version": "assertion-matrix-check-v1", "status": "passed" if result["valid"] else "blocked", "report": str(args.report), "errors": result["errors"], "matrix_sha256": result.get("matrix_sha256")}
    payload["check_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps(payload, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
