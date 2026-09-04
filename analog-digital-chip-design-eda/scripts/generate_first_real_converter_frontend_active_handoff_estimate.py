#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
FRONTEND = EVIDENCE / "sky130-ultra-sense-frontend-candidate.json"
INPUT_STAGE = EVIDENCE / "sky130-comparator-input-stage-ngspice.json"
MEASUREMENTS = LAB / "measurements"
OUT_JSON = EVIDENCE / "first-real-converter-frontend-active-handoff-estimate.json"
OUT_MD = EVIDENCE / "first-real-converter-frontend-active-handoff-estimate.md"
OUT_CSV = MEASUREMENTS / "first-real-converter-frontend-active-handoff-estimate.csv"

CANDIDATE_ID = "aimc_readout_candidate_001"
RUN_ID = "aimc_readout_candidate_001_frontend_active_handoff_estimate_run001"


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def measured_gain(input_stage: dict[str, Any]) -> float:
    gains = [
        abs(float(row["gain_v_per_v"]))
        for row in input_stage.get("rows", [])
        if row.get("ngspice_returncode") == 0
        and row.get("ngspice_timed_out") is False
        and row.get("polarity_correct") is True
        and row.get("gain_v_per_v") is not None
    ]
    if not gains:
        raise ValueError("no measured input-stage gain rows found")
    return min(gains)


def build_report() -> dict[str, Any]:
    frontend = json.loads(FRONTEND.read_text(encoding="utf-8"))
    input_stage = json.loads(INPUT_STAGE.read_text(encoding="utf-8"))
    gain = measured_gain(input_stage)
    rows = []
    for source in frontend.get("rows", []):
        if source.get("sign_preserved") is not True:
            continue
        frontend_sense_diff_v = float(source["sense_diff_after_v"])
        estimated_output_diff_v = frontend_sense_diff_v * gain
        rows.append(
            {
                "source_reset_mode": source["reset_mode"],
                "source_input_diff_mv": source["input_diff_mv"],
                "frontend_sample_diff_v": source["sample_diff_after_v"],
                "frontend_sense_diff_v": frontend_sense_diff_v,
                "input_stage_gain_v_per_v": gain,
                "estimated_output_diff_v": estimated_output_diff_v,
                "estimated_output_diff_mv": estimated_output_diff_v * 1000.0,
                "expected_sign": source["expected_sign"],
                "estimated_sign": 1 if estimated_output_diff_v > 0 else -1 if estimated_output_diff_v < 0 else 0,
                "estimated_polarity_correct": (1 if estimated_output_diff_v > 0 else -1 if estimated_output_diff_v < 0 else 0) == source["expected_sign"],
                "estimate_level": "derived_from_extracted_frontend_measurement_and_separate_measured_input_stage_gain",
            }
        )
    polarity_pass_count = sum(1 for row in rows if row["estimated_polarity_correct"])
    min_estimated_output_diff_v = min((abs(float(row["estimated_output_diff_v"])) for row in rows), default=0.0)
    return {
        "result_type": "first_real_converter_frontend_active_handoff_estimate",
        "status": "frontend_active_handoff_estimate_ready_not_same_deck_or_strict_evidence",
        "candidate_id": CANDIDATE_ID,
        "run_id": RUN_ID,
        "source_frontend_evidence": rel(FRONTEND),
        "source_input_stage_evidence": rel(INPUT_STAGE),
        "source_frontend_candidate": frontend.get("candidate_name"),
        "input_stage_topology": input_stage.get("topology"),
        "minimum_measured_input_stage_gain_v_per_v": gain,
        "case_count": len(rows),
        "estimated_polarity_pass_count": polarity_pass_count,
        "minimum_frontend_sense_diff_v": min((abs(float(row["frontend_sense_diff_v"])) for row in rows), default=0.0),
        "minimum_estimated_output_diff_v": min_estimated_output_diff_v,
        "uses_same_deck_simulation": False,
        "uses_same_extracted_layout_netlist": False,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "csv": rel(OUT_CSV),
        "strict_blockers": [
            "The frontend and active input stage are still separate evidence artifacts, not one extracted netlist simulated in one deck.",
            "The estimate multiplies measured frontend sense voltage by separately measured input-stage gain; it does not replace a direct transistor-level handoff run.",
            "There is no clocked latch resolution, kickback, mismatch, noise, SAR loop, supply-current integration, DRC/LVS area, or same-run break-even payload.",
        ],
        "claim_boundary": {
            "allowed": "estimates whether the measured frontend output is large enough for a previously measured Sky130 input-stage gain to make a millivolt-level signal",
            "not_allowed": "does not prove same-deck active handoff, full comparator behavior, full converter behavior, accepted post-layout evidence, or replacement economics",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in report["rows"] for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# First Real Converter Frontend Active Handoff Estimate",
        "",
        f"- status: `{report['status']}`",
        f"- candidate id: `{report['candidate_id']}`",
        f"- run id: `{report['run_id']}`",
        f"- source frontend evidence: `{report['source_frontend_evidence']}`",
        f"- source input-stage evidence: `{report['source_input_stage_evidence']}`",
        f"- minimum measured input-stage gain V/V: `{report['minimum_measured_input_stage_gain_v_per_v']:.6f}`",
        f"- minimum frontend sense diff V: `{report['minimum_frontend_sense_diff_v']:.9e}`",
        f"- minimum estimated output diff V: `{report['minimum_estimated_output_diff_v']:.9e}`",
        f"- estimated polarity pass count: `{report['estimated_polarity_pass_count']}` of `{report['case_count']}`",
        f"- uses same-deck simulation: `{report['uses_same_deck_simulation']}`",
        f"- uses same extracted layout netlist: `{report['uses_same_extracted_layout_netlist']}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A small voltage difference is useful only if the next circuit can make it larger without flipping its sign. The extracted frontend gives the small voltage. The transistor input-stage run gives a measured small-signal gain. Multiplying them answers one limited question: if the input stage behaved the same way at the frontend output, how large would the next electrical state become?",
        "",
        "This is not a new circuit simulation. It is a consistency check between two measured local artifacts. It says the passive frontend's roughly 67 microvolt sense signal would become about 0.62 millivolt after the measured input-stage gain. That is enough to justify building a real combined frontend-plus-input-stage deck. It is not enough to accept the converter.",
        "",
        "## Result",
        "",
        "| reset mode | frontend sense diff uV | estimated output diff mV | estimated polarity correct |",
        "|---|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['source_reset_mode']}` | `{float(row['frontend_sense_diff_v']) * 1_000_000.0:.6f}` | `{float(row['estimated_output_diff_mv']):.6f}` | `{row['estimated_polarity_correct']}` |"
        )
    lines.extend(["", "## Strict Blockers", ""])
    lines.extend(f"- {item}" for item in report["strict_blockers"])
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("first_real_converter_frontend_active_handoff_estimate")
    print(f"status,{report['status']}")
    print(f"candidate_id,{report['candidate_id']}")
    print(f"case_count,{report['case_count']}")
    print(f"minimum_measured_input_stage_gain_v_per_v,{report['minimum_measured_input_stage_gain_v_per_v']:.6f}")
    print(f"minimum_estimated_output_diff_v,{report['minimum_estimated_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
