#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
SIGN = EVIDENCE / "sky130-balanced-frontend-sign-preservation.json"
LATCH = EVIDENCE / "sky130-clocked-comparator-latch-ngspice.json"
OUT_JSON = EVIDENCE / "sky130-balanced-frontend-latch-decision.json"
OUT_MD = EVIDENCE / "sky130-balanced-frontend-latch-decision.md"
OUT_CSV = MEASUREMENTS / "sky130-balanced-frontend-latch-decision.csv"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Balanced Frontend Latch Decision",
        "",
        f"- status: `{report['status']}`",
        f"- extracted frontend sign-preserved cases: `{report['sign_preserved_case_count']}` of `{report['case_count']}`",
        f"- minimum absolute sense differential V: `{report['minimum_abs_sense_diff_v']:.9e}`",
        f"- ideal latch input target V: `{report['ideal_latch_input_target_v']:.9e}`",
        f"- minimum sense-to-latch-input ratio: `{report['minimum_sense_to_latch_input_ratio']:.6f}`",
        f"- accepted ready now: `{report['accepted_ready_now']}`",
        "",
        "## First Principle",
        "",
        "The extracted balanced frontend now preserves sign, but a sign is not the same as a digital decision. A latch needs enough input difference before its positive feedback starts. If the frontend gives the latch a much smaller difference than the already-tested latch target, the correct claim is not that the comparator works. The correct claim is that the sense handoff is promising but too small to accept without a real latch rerun.",
        "",
        "This page compares two measured objects. The earlier latch proxy passed when driven by the full target-edge input difference. The extracted balanced frontend gives only the sense-node difference measured after extraction. That sense difference is roughly one-tenth of the latch target, so latch decision remains an open gate.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | sense diff after V | sign preserved | sense-to-latch-target ratio |",
        "|---|---:|---:|---|---:|",
    ]
    for row in report["rows"]:
        lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['sense_diff_after_v']:.9e}` | `{row['sign_preserved']}` | `{row['sense_to_latch_input_ratio']:.6f}` |")
    lines.extend([
        "",
        "## Next Gate",
        "",
        "The next proof has to either strengthen the extracted sense-node differential or rerun a bounded latch fixture that resolves from this smaller sense-node input. Until then, the digital governor cannot treat this frontend as accepted comparator evidence.",
        "",
        "## Refused Claim",
        "",
        report["claim_boundary"]["not_allowed"],
        "",
    ])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    sign = json.loads(SIGN.read_text(encoding="utf-8"))
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    latch_target_v = abs(float(latch["target_combined_offset_noise_mv"])) / 1000.0
    rows = []
    for row in sign["rows"]:
        sense = float(row["sense_diff_after_v"])
        rows.append({
            "reset_mode": row["reset_mode"],
            "input_diff_mv": row["input_diff_mv"],
            "expected_sign": row["expected_sign"],
            "measured_sense_sign": row["measured_sense_sign"],
            "sense_diff_after_v": sense,
            "sign_preserved": row["sign_preserved"],
            "sense_to_latch_input_ratio": abs(sense) / latch_target_v if latch_target_v else 0.0,
        })
    min_sense = min(abs(row["sense_diff_after_v"]) for row in rows)
    min_ratio = min(row["sense_to_latch_input_ratio"] for row in rows)
    sign_count = sum(1 for row in rows if row["sign_preserved"] is True)
    report = {
        "result_type": "sky130_balanced_frontend_latch_decision",
        "status": "balanced_frontend_latch_decision_open_sense_signal_too_small",
        "source_sign_preservation": "evidence/aimc-simulator-adapters/sky130-balanced-frontend-sign-preservation.json",
        "source_ideal_latch_proxy": "evidence/aimc-simulator-adapters/sky130-clocked-comparator-latch-ngspice.json",
        "csv": rel(OUT_CSV),
        "case_count": len(rows),
        "sign_preserved_case_count": sign_count,
        "minimum_abs_sense_diff_v": min_sense,
        "ideal_latch_input_target_v": latch_target_v,
        "minimum_sense_to_latch_input_ratio": min_ratio,
        "latch_decision_proven": False,
        "rows": rows,
        "accepted_ready_now": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "compares the extracted balanced sense-node signal against the input size used by the passing latch proxy",
            "not_allowed": "does not prove latch resolution from the extracted sense nodes, extracted latch layout, active reset devices, comparator offset, comparator noise, DRC/LVS, SAR conversion, or accepted post-layout converter evidence",
        },
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print("sky130_balanced_frontend_latch_decision")
    print(f"status,{report['status']}")
    print(f"sign_preserved_case_count,{sign_count}")
    print(f"minimum_sense_to_latch_input_ratio,{min_ratio:.6f}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
