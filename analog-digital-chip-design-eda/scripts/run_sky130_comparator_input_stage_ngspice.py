#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
DECK_OUT = SPICE_DIR / "sky130_comparator_input_stage.sp"
CSV_OUT = MEASUREMENTS / "sky130-comparator-input-stage-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-input-stage-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-input-stage-ngspice.md"
SPEC_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-comparator-acceptance-fixture-spec.json"
NGSPICE_TIMEOUT_S = 120


@dataclass(frozen=True)
class Case:
    name: str
    diff_mv: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s*=\s*([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def read_op_node(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.match(rf"\s*{re.escape(name)}\s+([-+0-9.eE]+)\s*$", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice OP node {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    diff_v = case.diff_mv / 1000.0
    vinp = 0.9 + diff_v / 2.0
    vinn = 0.9 - diff_v / 2.0
    return f"""* Sky130 comparator input-stage polarity proxy.
* This is a transistor differential-pair input stage with ideal bias and resistive loads.
* It is not a clocked latch and not a noise simulation.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=8.0
.param vinp={vinp:.12f}
.param vinn={vinn:.12f}
.param rd=100k
.param itail=20u

VDD vdd 0 {{vdd}}
VINP inp 0 {{vinp}}
VINN inn 0 {{vinn}}
RDP vdd outp {{rd}}
RDN vdd outn {{rd}}
XINP outp inp tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XINN outn inn tail 0 sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
ITAIL tail 0 {{itail}}
COUTP outp 0 2f
COUTN outn 0 2f

.op
.control
op
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    try:
        result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "input_diff_mv": case.diff_mv,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "polarity_correct": False,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    outp_v = read_op_node(result.stdout, "outp")
    outn_v = read_op_node(result.stdout, "outn")
    output_diff_v = outn_v - outp_v
    expected_sign = 1 if case.diff_mv > 0 else -1 if case.diff_mv < 0 else 0
    measured_sign = 1 if output_diff_v > 0 else -1 if output_diff_v < 0 else 0
    return {
        "case": case.name,
        "input_diff_mv": case.diff_mv,
        "input_common_mode_v": 0.9,
        "outp_v": outp_v,
        "outn_v": outn_v,
        "tail_v": read_op_node(result.stdout, "tail"),
        "output_diff_v": output_diff_v,
        "gain_v_per_v": output_diff_v / (case.diff_mv / 1000.0) if case.diff_mv else None,
        "expected_sign": expected_sign,
        "measured_sign": measured_sign,
        "polarity_correct": expected_sign == measured_sign,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def estimate_zero_crossing(rows: list[dict[str, Any]]) -> float | None:
    measured = sorted((row for row in rows if not row.get("ngspice_timed_out")), key=lambda row: float(row["input_diff_mv"]))
    for left, right in zip(measured, measured[1:]):
        y0 = float(left["output_diff_v"])
        y1 = float(right["output_diff_v"])
        if y0 == 0:
            return float(left["input_diff_mv"])
        if y0 * y1 <= 0 and y1 != y0:
            x0 = float(left["input_diff_mv"])
            x1 = float(right["input_diff_mv"])
            return x0 - y0 * (x1 - x0) / (y1 - y0)
    return None


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    spec = json.loads(SPEC_JSON.read_text(encoding="utf-8"))
    budget = spec["derived_budget"]
    target_mv = float(budget["target_combined_offset_noise_mv"])
    hard_budget_mv = float(budget["remaining_comparator_offset_or_noise_budget_mv"])
    cases = [
        Case("negative_hard_budget_edge", -hard_budget_mv),
        Case("negative_target_edge", -target_mv),
        Case("negative_half_target", -target_mv / 2.0),
        Case("positive_half_target", target_mv / 2.0),
        Case("positive_target_edge", target_mv),
        Case("positive_hard_budget_edge", hard_budget_mv),
    ]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    zero_crossing_mv = estimate_zero_crossing(rows)
    polarity_pass_count = sum(1 for row in rows if row["polarity_correct"])
    all_polarity_pass = polarity_pass_count == len(rows)
    offset_proxy_pass = zero_crossing_mv is not None and abs(zero_crossing_mv) <= target_mv
    return {
        "result_type": "sky130_comparator_input_stage_ngspice",
        "status": "sky130_comparator_input_stage_polarity_proxy_passed_not_latch_or_noise_proof" if all_polarity_pass and offset_proxy_pass else "sky130_comparator_input_stage_polarity_proxy_failed",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8"],
        "topology": "resistively_loaded_sky130_nfet_differential_pair_with_ideal_tail_bias",
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "target_combined_offset_noise_mv": target_mv,
        "hard_budget_mv": hard_budget_mv,
        "estimated_static_zero_crossing_mv": zero_crossing_mv,
        "polarity_pass_count": polarity_pass_count,
        "all_cases_correct_polarity": all_polarity_pass,
        "offset_proxy_passes_target": offset_proxy_pass,
        "rows": rows,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "runs a Sky130 transistor differential input stage and checks whether tiny positive and negative differential inputs produce the correct output polarity around the measured comparator budget",
            "not_allowed": "does not prove a clocked comparator latch, comparator noise, kickback, metastability, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Comparator Input-Stage Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- target combined offset/noise mV: `{report['target_combined_offset_noise_mv']:.4f}`",
        f"- hard budget mV: `{report['hard_budget_mv']:.4f}`",
        f"- estimated static zero crossing mV: `{fmt(report['estimated_static_zero_crossing_mv'])}`",
        f"- polarity pass count: `{report['polarity_pass_count']}` of `{report['case_count']}`",
        f"- all cases correct polarity: `{report['all_cases_correct_polarity']}`",
        f"- offset proxy passes target: `{report['offset_proxy_passes_target']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A comparator starts as a sign test. Two nearby voltages enter a circuit. The circuit must turn the larger one into the correct side of an output difference.",
        "",
        "This fixture tests only that first piece. It uses a Sky130 nfet differential pair with ideal tail bias and resistive loads. The input difference is swept around the tiny budget left by the measured sample-and-hold candidate. If the output polarity flips at the right place, the input stage is at least pointing in the correct direction.",
        "",
        "This is much weaker than a real ADC comparator. It is not a clocked latch. A real comparator must latch, reject kickback, resolve before the SAR bit deadline, and survive device mismatch and noise. This page exists to make the next transistor step executable without pretending that a simple input pair is the finished decision circuit.",
        "",
        "## Results",
        "",
        "| case | input diff mV | outp V | outn V | output diff V | gain V/V | polarity correct |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | timeout | timeout | timeout | timeout | `False` |")
            continue
        gain = "not measured" if row["gain_v_per_v"] is None else f"{row['gain_v_per_v']:.6f}"
        lines.append(
            f"| `{row['case']}` | `{row['input_diff_mv']:.6f}` | `{row['outp_v']:.9f}` | `{row['outn_v']:.9f}` | `{row['output_diff_v']:.9e}` | `{gain}` | `{row['polarity_correct']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_comparator_input_stage_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"polarity_pass_count,{report['polarity_pass_count']}")
    print(f"estimated_static_zero_crossing_mv,{report['estimated_static_zero_crossing_mv']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0 if report["status"] == "sky130_comparator_input_stage_polarity_proxy_passed_not_latch_or_noise_proof" else 1


if __name__ == "__main__":
    raise SystemExit(main())
