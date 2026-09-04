#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SOURCE_JSON = EVIDENCE / "sky130-swapped-latch-clock-timing-debug.json"
CSV_OUT = LAB / "measurements" / "sky130-clocked-latch-output-convention-diagnostic.csv"
OUT_JSON = EVIDENCE / "sky130-clocked-latch-output-convention-diagnostic.json"
OUT_MD = EVIDENCE / "sky130-clocked-latch-output-convention-diagnostic.md"


def sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def build_report() -> dict[str, Any]:
    source = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for row in source["rows"]:
        outn_minus_outp = float(row["outn_final_v"]) - float(row["outp_final_v"])
        outp_minus_outn = -outn_minus_outp
        expected_sign = int(row["expected_sign"])
        rows.append(
            {
                "case": row["case"],
                "input_diff_mv": row["input_diff_mv"],
                "clk_start_ns": row["clk_start_ns"],
                "outp_final_v": row["outp_final_v"],
                "outn_final_v": row["outn_final_v"],
                "expected_sign": expected_sign,
                "outn_minus_outp_v": outn_minus_outp,
                "outn_minus_outp_sign": sign(outn_minus_outp),
                "outn_minus_outp_matches_contract": sign(outn_minus_outp) == expected_sign and abs(outn_minus_outp) >= 0.9,
                "outp_minus_outn_v": outp_minus_outn,
                "outp_minus_outn_sign": sign(outp_minus_outn),
                "outp_minus_outn_matches_contract": sign(outp_minus_outn) == expected_sign and abs(outp_minus_outn) >= 0.9,
            }
        )
    raw_matches = sum(1 for row in rows if row["outn_minus_outp_matches_contract"])
    inverted_matches = sum(1 for row in rows if row["outp_minus_outn_matches_contract"])
    inferred = inverted_matches == len(rows) and raw_matches == 0
    return {
        "result_type": "sky130_clocked_latch_output_convention_diagnostic",
        "status": "clocked_latch_output_convention_inversion_confirmed" if inferred else "clocked_latch_output_convention_still_ambiguous",
        "source_clock_timing": rel(SOURCE_JSON),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "outn_minus_outp_contract_match_count": raw_matches,
        "outp_minus_outn_contract_match_count": inverted_matches,
        "inferred_clocked_latch_output_contract": "digital_bit_positive_when_outp_exceeds_outn" if inferred else "unresolved",
        "requires_new_ngspice_run": False,
        "uses_existing_same_run_measurements": True,
        "uses_sampled_nodes": False,
        "accepted_post_layout_written": False,
        "strict_payload_ready": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "reinterprets the measured clocked-latch rails under both digital output conventions and identifies the convention that matches the source polarity contract",
            "not_allowed": "does not change the circuit, prove sampled-node kickback, prove coupled preamp/latch loading, prove SAR bit cycling, and does not create accepted post-layout converter evidence",
        },
    }


def write_outputs(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Sky130 Clocked Latch Output Convention Diagnostic",
        "",
        f"- status: `{report['status']}`",
        f"- case count: `{report['case_count']}`",
        f"- outn-minus-outp contract match count: `{report['outn_minus_outp_contract_match_count']}`",
        f"- outp-minus-outn contract match count: `{report['outp_minus_outn_contract_match_count']}`",
        f"- inferred clocked latch output contract: `{report['inferred_clocked_latch_output_contract']}`",
        f"- requires new ngspice run: `{report['requires_new_ngspice_run']}`",
        f"- uses existing same-run measurements: `{report['uses_existing_same_run_measurements']}`",
        f"- uses sampled nodes: `{report['uses_sampled_nodes']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        "",
        "## First Principle",
        "",
        "A latch has two analog rails. A digital bit is created only after we name which rail means the positive decision.",
        "",
        "The clocked timing run did not show a weak latch. The rail separation is large in every case. The failure is that the report called `outn - outp` the signed output, while the measured rails match the source polarity contract when the digital output is defined as `outp - outn`.",
        "",
        "That fixes the next work item. Before adding sampled-node kickback, the converter contract must name the latch output bit explicitly: positive source difference means `outp` high and `outn` low.",
        "",
        "## Convention Check",
        "",
        "| case | clock ns | expected sign | outn-outp matches | outp-outn matches |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['case']}` | `{row['clk_start_ns']}` | `{row['expected_sign']}` | `{row['outn_minus_outp_matches_contract']}` | `{row['outp_minus_outn_matches_contract']}` |"
        )
    lines.extend(["", "## Boundary", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print("sky130_clocked_latch_output_convention_diagnostic")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"outn_minus_outp_contract_match_count,{report['outn_minus_outp_contract_match_count']}")
    print(f"outp_minus_outn_contract_match_count,{report['outp_minus_outn_contract_match_count']}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
