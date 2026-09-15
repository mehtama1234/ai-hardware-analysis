#!/usr/bin/env python3
"""Build a conservative transfer table from retained local four-bit receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PRODUCT_ROOT = Path(__file__).resolve().parents[3]
EDA_EVIDENCE = PRODUCT_ROOT / "analog-digital-chip-design-eda/evidence/aimc-simulator-adapters"
CANDIDATES = {
    1: "local-fourbit-code1-79ns-20ps.json",
    8: "local-fourbit-code8-79ns-20ps-dummy1p.json",
    10: "local-fourbit-code10-79ns-30ps-dummy1p.json",
    13: "local-fourbit-code13-79ns-50ps-transistor-handoff-pmosbank4.json",
    14: "local-fourbit-code14-79ns-30ps-dummy1p.json",
    15: "local-fourbit-code15-79ns-20ps.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = {}
    sources = []
    for code, filename in CANDIDATES.items():
        path = EDA_EVIDENCE / filename
        receipt = json.loads(path.read_text(encoding="utf-8"))
        row = receipt["rows"][0]
        rows[str(code)] = {
            "code": code,
            "source_file": str(path),
            "source_sha256": digest(path),
            "measured": row.get("measured") is True,
            "status": receipt.get("status"),
            "top_settled_v": row.get("top_settled_v"),
            "expected_top_v": row.get("expected_top_v"),
            "settling_error_v": row.get("settling_error_v"),
            "bottom_plate_v": row.get("bottom_plate_v"),
            "bottom_plates_legal": receipt.get("all_bottom_plates_legal", True),
            "within_half_lsb": receipt.get("all_codes_within_half_lsb", False),
        }
        sources.append({"path": str(path), "sha256": digest(path)})
    requested = list(range(16))
    present = sorted(int(code) for code in rows)
    missing = [code for code in requested if code not in present]
    output = {
        "schema_version": "sky130-circuit-transfer-table-v0.1",
        "result_type": "local_circuit_derived_partial_transfer_table",
        "requested_code_count": 16,
        "measured_code_count": len(present),
        "present_codes": present,
        "missing_codes": missing,
        "complete_code_map": not missing,
        "rows": rows,
        "sources": sources,
        "adapter_binding": {"status": "refused_incomplete_code_map", "bound_to_workload": False,
                             "reason": "a complete 16-code transfer table and declared state/reset semantics are required"},
        "analog_authorized": False,
        "claim_boundary": "Local circuit-derived partial code table only; incomplete map is not an ADC profile, hardware yield, or analog authorization.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    report_path = args.output / "circuit_transfer_table.json"
    report_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (args.output / "manifest.json").write_text(json.dumps({"files": [
        {"path": str(report_path), "sha256": digest(report_path)},
        *sources,
        {"path": str(Path(__file__)), "sha256": digest(Path(__file__))},
    ]}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(report_path), "measured_code_count": len(present), "missing_codes": missing,
                      "bound_to_workload": False}, sort_keys=True))


if __name__ == "__main__":
    main()
