#!/usr/bin/env python3
"""Inventory executable behavioral contracts for the real multi-module targets."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text())
    records = []
    for design in catalog.get("designs", []):
        root = Path(design["root"])
        files = sorted(
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file()
            and not any(part in {"runs", "results", "tmp", "issue_reproducible"} for part in path.relative_to(root).parts)
            and path.suffix.lower() in {".v", ".sv", ".py", ".tcl"}
            and ("tb" in path.name.lower() or "test" in path.name.lower() or "sim" in path.name.lower())
        )
        local_root = ROOT / "evidence/heldout-behavioral-contracts" / design["top"]
        local_files = sorted(str(path.relative_to(ROOT)) for path in local_root.rglob("*") if path.is_file()) if local_root.is_dir() else []
        records.append(
            {
                "top": design["top"],
                "repository": design["repository"],
                "root": str(root),
                "compiled": design.get("compile_status") == "passed",
                "testlike_files": files,
                "local_contract_files": local_files,
                "behavioral_contract_status": "available" if files or local_files else "missing",
            }
        )
    available = sum(item["behavioral_contract_status"] == "available" for item in records)
    report = {
        "schema_version": "heldout-behavioral-contract-inventory-v1",
        "catalog": str(args.catalog.resolve()),
        "catalog_sha256": hashlib.sha256(args.catalog.read_bytes()).hexdigest(),
        "target_count": len(records),
        "compiled_target_count": sum(item["compiled"] for item in records),
        "behavioral_contract_count": available,
        "missing_behavioral_contract_count": len(records) - available,
        "status": "ready_for_heldout_execution" if available == len(records) else "blocked_pending_behavioral_contracts",
        "targets": records,
        "claim_boundary": "compile and structural evidence do not establish a behavioral contract; held-out semantic localization remains unmeasured until each target has an executable contract and mutation replay",
    }
    report["report_sha256"] = digest(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": report["status"], "target_count": len(records), "behavioral_contract_count": available}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
