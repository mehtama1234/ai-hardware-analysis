#!/usr/bin/env python3
"""Independently verify the register repair review and retest artifact."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("review", type=Path); parser.add_argument("--model-report", type=Path, required=True); parser.add_argument("--source", type=Path, required=True); args = parser.parse_args()
    review = json.loads(args.review.read_text(encoding="utf-8")); model = json.loads(args.model_report.read_text(encoding="utf-8")); errors = []
    if review.get("schema_version") != "llm-approved-register-repair-v1" or review.get("design_id") != "register_peripheral": errors.append("unexpected register repair schema or design")
    repair = review.get("repair", {}); raw = (model.get("register_repair_run") or {}).get("raw_output", {})
    if repair.get("before") != "else if (wr_en) control <= wdata;" or repair.get("after") != "else if (wr_en && addr == 2'd0) control <= wdata;" or repair.get("model_generated") is not True: errors.append("bounded model-generated edit is incorrect")
    if review.get("source", {}).get("sha256") != digest(args.source): errors.append("canonical source changed")
    if raw.get("before") != repair.get("before") or raw.get("after") != repair.get("after"): errors.append("review does not match raw model choice")
    if review.get("approval", {}).get("status") == "approved" and (repair.get("decision") != "allowed" or review.get("retest", {}).get("status") != "passed" or review.get("retest", {}).get("original_unchanged") is not True): errors.append("approved retest is incomplete")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(json.dumps({"status": "passed", "design": "register_peripheral", "canonical_source_unchanged": True})); return 0

if __name__ == "__main__":
    raise SystemExit(main())
