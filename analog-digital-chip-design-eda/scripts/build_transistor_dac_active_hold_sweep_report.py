#!/usr/bin/env python3
"""Aggregate active-hold diagnostics without promoting them to qualification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
OUT_JSON = EVIDENCE / "sky130-transistor-dac-active-hold-sweep.json"
OUT_MD = EVIDENCE / "sky130-transistor-dac-active-hold-sweep.md"

RECEIPTS = (
    "local-fourbit-code14-79ns-50ps-activehold35w4.json",
    "local-fourbit-code14-79ns-50ps-activehold45w1.json",
    "local-fourbit-code14-79ns-50ps-activehold45w4.json",
    "local-fourbit-code14-79ns-50ps-activehold65w4.json",
    "local-fourbit-code14-79ns-50ps-activehold65w16.json",
    "local-fourbit-code14-79ns-50ps-activehold65w16l1.json",
    "local-fourbit-code13-79ns-50ps-activehold45w4.json",
)


def load_receipt(name: str) -> dict:
    path = EVIDENCE / name
    if not path.is_file():
        raise SystemExit(f"missing active-hold receipt: {path}")
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "report": json.loads(path.read_text(encoding="utf-8")),
    }


def main() -> int:
    receipts = [load_receipt(name) for name in RECEIPTS]
    rows = []
    for item in receipts:
        report = item["report"]
        measured = [row for row in report.get("rows", []) if row.get("measured")]
        row = {
            "source": item["path"],
            "sha256": item["sha256"],
            "requested_codes": report.get("requested_codes", []),
            "measured_code_count": report.get("measured_code_count", 0),
            "status": report.get("status"),
            "active_hold": report.get("active_hold", False),
            "active_hold_ns": report.get("active_hold_ns"),
            "active_hold_width_um": report.get("active_hold_width_um"),
            "active_hold_length_um": report.get("active_hold_length_um"),
            "all_codes_within_half_lsb": report.get("all_codes_within_half_lsb", False),
            "all_bottom_plates_legal": report.get("all_bottom_plates_legal", False),
            "max_settling_error_v": report.get("max_settling_error_v"),
            "measured_rows": measured,
        }
        rows.append(row)

    measured_rows = [row for row in rows if row["measured_rows"]]
    def rail_error(row: dict) -> float:
        sample = row["measured_rows"][0]
        code = int(sample["code"])
        values = sample.get("bottom_plate_v", [])
        return max(
            abs(value - (1.8 if (code >> (3 - bit)) & 1 else 0.0))
            for bit, value in enumerate(values)
        ) if values else float("inf")

    best = min(measured_rows, key=rail_error) if measured_rows else None
    report = {
        "result_type": "sky130_transistor_dac_active_hold_sweep",
        "status": "active_hold_sweep_diagnostic_physical_qualification_open",
        "receipt_count": len(rows),
        "measured_receipt_count": len(measured_rows),
        "rows": rows,
        "best_by_max_absolute_bottom_plate_value": best["source"] if best else None,
        "decision": {
            "selected_candidate": "minimum-length active hold with late enable; not accepted",
            "reason": "active hold improves transfer trajectory but every tested candidate leaves an illegal rail or fails numerical convergence",
            "next_required_change": "new bottom-plate switch cell with independent transfer and hold paths, then full 16-code/PVT/mismatch campaign",
        },
        "claim_boundary": {
            "allowed": "compares named Sky130 transistor DAC diagnostic receipts and preserves their hashes",
            "not_allowed": "does not establish converter qualification, SAR correctness, workload accuracy, energy advantage, silicon yield, or analog authorization",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Transistor DAC Active-Hold Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- receipts: `{report['measured_receipt_count']}` measured of `{report['receipt_count']}`",
        "",
        "| source | code | hold ns | width um | length um | top error V | legal | status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        measured = row["measured_rows"]
        code = measured[0].get("code", "timeout") if measured else "timeout"
        lines.append(
            f"| `{Path(row['source']).name}` | {code} | {row['active_hold_ns']} | "
            f"{row['active_hold_width_um']} | {row['active_hold_length_um']} | "
            f"{row['max_settling_error_v']} | {row['all_bottom_plates_legal']} | `{row['status']}` |"
        )
    lines += [
        "",
        "The sweep is diagnostic only. A measured code subset cannot become a converter profile, and a top-plate half-LSB result cannot override illegal internal nodes or numerical timeouts.",
        "",
        "## Next required change",
        "",
        report["decision"]["next_required_change"],
        "",
        "## Refused claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"status,{report['status']}")
    print(f"receipts,{report['measured_receipt_count']}/{report['receipt_count']}")
    print(f"best_by_abs_bottom_plate,{report['best_by_max_absolute_bottom_plate_value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
