#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
DECK_OUT = SPICE_DIR / "sky130_differential_dummy_candidate_input_sweep.sp"
CSV_OUT = MEASUREMENTS / "sky130-differential-dummy-candidate-input-sweep.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-input-sweep.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-differential-dummy-candidate-input-sweep.md"
NGSPICE_TIMEOUT_S = 180


@dataclass(frozen=True)
class Case:
    name: str
    common_mode_v: float
    diff_v: float


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


def build_deck(case: Case) -> str:
    vinp = case.common_mode_v + case.diff_v / 2.0
    vinn = case.common_mode_v - case.diff_v / 2.0
    return f"""* Sky130 differential dummy-cancellation candidate input sweep.
* Fixed 0.50x dummy devices are tested at low, mid, and high common-mode points.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param wp=4.0
.param dummy_wn=1.0
.param dummy_wp=2.0
.param csample=0.2p
.param cload=0.05p
.param vinp={vinp}
.param vinn={vinn}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VINP inp 0 PULSE(0 {{vinp}} 0.1n 20p 20p 20n 40n)
VINN inn 0 PULSE(0 {{vinn}} 0.1n 20p 20p 20n 40n)
VCTRL ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
VCTRLB ctrlb 0 PULSE({{vdd}} 0 0.2n 20p 20p 7n 20n)

XSWNP inp ctrl sp vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPP inp ctrlb sp vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XSWNN inn ctrl sn vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
XSWPN inn ctrlb sn vdd sky130_fd_pr__pfet_01v8 W={{wp}} L={{lmin}}
XDUMNP sp ctrlb sp vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPP sp ctrl sp vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}
XDUMNN sn ctrlb sn vss sky130_fd_pr__nfet_01v8 W={{dummy_wn}} L={{lmin}}
XDUMPN sn ctrl sn vdd sky130_fd_pr__pfet_01v8 W={{dummy_wp}} L={{lmin}}

CSP sp 0 {{csample}}
CSN sn 0 {{csample}}
CLP sp 0 {{cload}}
CLN sn 0 {{cload}}
RLEAKP sp 0 100G
RLEAKN sn 0 100G

.tran 2p 10n
.measure tran acquired_p_v FIND v(sp) AT=6.8n
.measure tran acquired_n_v FIND v(sn) AT=6.8n
.measure tran held_p_v FIND v(sp) AT=8.5n
.measure tran held_n_v FIND v(sn) AT=8.5n
.measure tran input_p_v FIND v(inp) AT=6.8n
.measure tran input_n_v FIND v(inn) AT=6.8n
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    deck = build_deck(case)
    DECK_OUT.write_text(deck, encoding="utf-8")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    with tempfile.TemporaryDirectory(prefix="aimc-differential-input-") as tmp:
        case_deck = Path(tmp) / "candidate.sp"
        case_deck.write_text(deck, encoding="utf-8")
        try:
            result = subprocess.run(["ngspice", "-b", str(case_deck)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=NGSPICE_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {
                "case": case.name,
                "common_mode_v": case.common_mode_v,
                "target_diff_v": case.diff_v,
                "ngspice_returncode": None,
                "ngspice_timed_out": True,
                "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
                "half_lsb_12b_v": half_lsb_12b_v,
                "pass_diff_hold_delta_half_lsb_12b": False,
                "pass_diff_total_error_half_lsb_12b": False,
            }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    input_p_v = read_measure(result.stdout, "input_p_v")
    input_n_v = read_measure(result.stdout, "input_n_v")
    acquired_p_v = read_measure(result.stdout, "acquired_p_v")
    acquired_n_v = read_measure(result.stdout, "acquired_n_v")
    held_p_v = read_measure(result.stdout, "held_p_v")
    held_n_v = read_measure(result.stdout, "held_n_v")
    input_diff_v = input_p_v - input_n_v
    acquired_diff_v = acquired_p_v - acquired_n_v
    held_diff_v = held_p_v - held_n_v
    diff_hold_abs_delta_v = abs(held_diff_v - acquired_diff_v)
    diff_total_abs_error_v = abs(input_diff_v - held_diff_v)
    row = {
        "case": case.name,
        "common_mode_v": case.common_mode_v,
        "target_diff_v": case.diff_v,
        "input_p_v": input_p_v,
        "input_n_v": input_n_v,
        "acquired_p_v": acquired_p_v,
        "acquired_n_v": acquired_n_v,
        "held_p_v": held_p_v,
        "held_n_v": held_n_v,
        "input_diff_v": input_diff_v,
        "acquired_diff_v": acquired_diff_v,
        "held_diff_v": held_diff_v,
        "p_hold_abs_delta_v": abs(held_p_v - acquired_p_v),
        "n_hold_abs_delta_v": abs(held_n_v - acquired_n_v),
        "diff_hold_abs_delta_v": diff_hold_abs_delta_v,
        "diff_total_abs_error_v": diff_total_abs_error_v,
        "half_lsb_12b_v": half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }
    row["pass_diff_hold_delta_half_lsb_12b"] = diff_hold_abs_delta_v <= half_lsb_12b_v
    row["pass_diff_total_error_half_lsb_12b"] = diff_total_abs_error_v <= half_lsb_12b_v
    return row


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    cases = [Case("low_cm_0p3_diff_0p2", 0.3, 0.2), Case("mid_cm_0p9_diff_0p2", 0.9, 0.2), Case("high_cm_1p5_diff_0p2", 1.5, 0.2)]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    worst_hold = max((row["diff_hold_abs_delta_v"] for row in measured), default=None)
    worst_total = max((row["diff_total_abs_error_v"] for row in measured), default=None)
    half_lsb = 1.8 / 4096.0 / 2.0
    return {
        "result_type": "sky130_differential_dummy_candidate_input_sweep",
        "status": "sky130_differential_dummy_candidate_input_sweep_characterized_not_converter_proof",
        "topology": "fixed_dummy_0p50x_differential_transmission_gate_sample_hold",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "half_lsb_12b_v": half_lsb,
        "rows": rows,
        "worst_diff_hold_abs_delta_v": worst_hold,
        "worst_diff_total_abs_error_v": worst_total,
        "diff_hold_pass_count": sum(1 for row in rows if row["pass_diff_hold_delta_half_lsb_12b"]),
        "diff_total_error_pass_count": sum(1 for row in rows if row["pass_diff_total_error_half_lsb_12b"]),
        "all_measured_cases_pass_diff_hold": bool(rows) and all(row["pass_diff_hold_delta_half_lsb_12b"] for row in rows),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "tests the fixed 0.50x differential dummy-cancellation sample-hold candidate across low, mid, and high common-mode inputs",
            "not_allowed": "does not prove comparator offset, noise, SAR conversion, mismatch, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Differential Dummy Candidate Input Sweep",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst differential hold abs delta V: `{fmt(report['worst_diff_hold_abs_delta_v'])}`",
        f"- worst differential total abs error V: `{fmt(report['worst_diff_total_abs_error_v'])}`",
        f"- differential hold pass count: `{report['diff_hold_pass_count']}` of `{report['case_count']}`",
        f"- all measured cases pass differential hold: `{report['all_measured_cases_pass_diff_hold']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A passing middle input can hide a weak circuit. MOS switch charge, overdrive, and body behavior change with voltage. A candidate sample-and-hold front end has to keep the decision voltage still at low, mid, and high input levels, not only where the cancellation happens to line up.",
        "",
        "This run fixes the best dummy size from the prior sweep and moves the common-mode input. The only question is whether the same cancellation still keeps the differential hold movement below the 12-bit half-LSB line.",
        "",
        "## Results",
        "",
        "| case | common mode V | input diff V | acquired diff V | held diff V | differential hold delta V | passes half LSB |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| `{row['case']}` | `{row['common_mode_v']:.3f}` | `{row['target_diff_v']:.3f}` | timeout | timeout | timeout | `False` |")
            continue
        lines.append(
            f"| `{row['case']}` | `{row['common_mode_v']:.3f}` | `{row['input_diff_v']:.9f}` | `{row['acquired_diff_v']:.9f}` | `{row['held_diff_v']:.9f}` | `{row['diff_hold_abs_delta_v']:.9e}` | `{row['pass_diff_hold_delta_half_lsb_12b']}` |"
        )
    lines.extend(
        [
            "",
            "## Reading",
            "",
            "If all three rows pass, the candidate has cleared the first useful breadth gate. The next proof is mismatch and noise. If any row fails, the dummy size is not a general solution; it is only a local cancellation point.",
            "",
            "## Refused Claim",
            "",
            report["claim_boundary"]["not_allowed"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_differential_dummy_candidate_input_sweep")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"worst_diff_hold_abs_delta_v,{fmt(report['worst_diff_hold_abs_delta_v'])}")
    print(f"diff_hold_pass_count,{report['diff_hold_pass_count']}")
    print(f"all_measured_cases_pass_diff_hold,{report['all_measured_cases_pass_diff_hold']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
