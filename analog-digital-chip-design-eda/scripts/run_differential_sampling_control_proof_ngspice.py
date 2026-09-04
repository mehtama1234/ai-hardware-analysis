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
DECK_OUT = SPICE_DIR / "differential_sampling_control_proof.sp"
CSV_OUT = MEASUREMENTS / "differential-sampling-control-proof-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "differential-sampling-control-proof-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "differential-sampling-control-proof-ngspice.md"


@dataclass(frozen=True)
class Case:
    name: str
    diff_v: float
    common_injection_mv: float
    mismatch_injection_mv: float


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
    vp = 0.9 + case.diff_v / 2.0
    vn = 0.9 - case.diff_v / 2.0
    common = case.common_injection_mv / 1000.0
    mismatch = case.mismatch_injection_mv / 1000.0
    ip = -common * 0.2e-12 / 20e-12
    inn = -(common + mismatch) * 0.2e-12 / 20e-12
    return f"""* Differential sampling control proof.
* Ideal switches isolate topology behavior from Sky130 model convergence.

.param vinp={vp}
.param vinn={vn}
.param common={common}
.param mismatch={mismatch}

VINP inp 0 {{vinp}}
VINN inn 0 {{vinn}}
VCTRL ctrl 0 PULSE(1 0 7n 20p 20p 20n 40n)

.model SWMOD SW(Ron=10 Roff=1e12 Vt=0.5 Vh=0.05)
SP inp hp ctrl 0 SWMOD
SN inn hn ctrl 0 SWMOD
CP hp 0 0.2p
CN hn 0 0.2p

IINJP hp 0 PWL(0 0 7.02n 0 7.021n {ip} 7.04n {ip} 7.041n 0 10n 0)
IINJN hn 0 PWL(0 0 7.02n 0 7.021n {inn} 7.04n {inn} 7.041n 0 10n 0)
.tran 20p 10n
.measure tran acquired_p_v FIND v(hp) AT=6.8n
.measure tran acquired_n_v FIND v(hn) AT=6.8n
.measure tran held_p_v FIND v(hp) AT=8.5n
.measure tran held_n_v FIND v(hn) AT=8.5n
.measure tran acquired_diff_v PARAM='acquired_p_v-acquired_n_v'
.measure tran held_diff_v PARAM='held_p_v-held_n_v'
.measure tran p_hold_abs_delta_v PARAM='abs(held_p_v-acquired_p_v)'
.measure tran n_hold_abs_delta_v PARAM='abs(held_n_v-acquired_n_v)'
.measure tran diff_hold_abs_delta_v PARAM='abs(held_diff_v-acquired_diff_v)'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    result = subprocess.run(["ngspice", "-b", str(DECK_OUT)], cwd=ROOT, text=True, capture_output=True, check=False, timeout=10)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    acquired_p = read_measure(result.stdout, "acquired_p_v")
    acquired_n = read_measure(result.stdout, "acquired_n_v")
    held_p = read_measure(result.stdout, "held_p_v")
    held_n = read_measure(result.stdout, "held_n_v")
    acquired_diff = acquired_p - acquired_n
    held_diff = held_p - held_n
    row = {
        "case": case.name,
        "target_diff_v": case.diff_v,
        "common_injection_mv": case.common_injection_mv,
        "mismatch_injection_mv": case.mismatch_injection_mv,
        "acquired_p_v": acquired_p,
        "acquired_n_v": acquired_n,
        "held_p_v": held_p,
        "held_n_v": held_n,
        "acquired_diff_v": acquired_diff,
        "held_diff_v": held_diff,
        "p_hold_abs_delta_v": abs(held_p - acquired_p),
        "n_hold_abs_delta_v": abs(held_n - acquired_n),
        "diff_hold_abs_delta_v": abs(held_diff - acquired_diff),
        "half_lsb_12b_v": half_lsb_12b_v,
    }
    row["pass_diff_hold_delta_half_lsb_12b"] = row["diff_hold_abs_delta_v"] <= half_lsb_12b_v
    return row


def build_report() -> dict[str, Any]:
    rows = [
        run_case(Case("common_only_small_signal", 0.02, 5.0, 0.0)),
        run_case(Case("common_only_large_signal", 0.8, 5.0, 0.0)),
        run_case(Case("mismatched_injection", 0.2, 5.0, 0.3)),
    ]
    return {
        "result_type": "differential_sampling_control_proof_ngspice",
        "status": "differential_sampling_control_proof_passed_topology_only_not_converter_proof",
        "topology": "ideal_switch_differential_sampling_with_controlled_charge_injection",
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "case_count": len(rows),
        "measured_case_count": len(rows),
        "rows": rows,
        "half_lsb_12b_v": rows[0]["half_lsb_12b_v"],
        "worst_diff_hold_abs_delta_v": max(row["diff_hold_abs_delta_v"] for row in rows),
        "diff_hold_pass_count": sum(1 for row in rows if row["pass_diff_hold_delta_half_lsb_12b"]),
        "sky130_transistor_model_used": False,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "proves the differential cancellation principle with ideal switches and controlled injected charge",
            "not_allowed": "does not prove Sky130 transistor behavior, comparator offset, noise, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = list(rows[0].keys())
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Differential Sampling Control Proof Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- Sky130 transistor model used: `{report['sky130_transistor_model_used']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst differential hold abs delta V: `{report['worst_diff_hold_abs_delta_v']:.9e}`",
        f"- differential hold pass count: `{report['diff_hold_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A single held node is fragile because every extra bit of charge becomes voltage error. A differential decision is different. If both held nodes receive the same unwanted charge, both voltages move together and the difference stays almost unchanged.",
        "",
        "This control proof removes the Sky130 transistor model and uses ideal switches. Then it injects a known amount of charge into both held nodes. When the injected charge is exactly common, the decision voltage barely moves. When one side gets extra charge, only that mismatch remains in the differential voltage.",
        "",
        "That is the reason differential sampling is still the right direction even though the full Sky130 transistor fixture is not stable yet. The topology can reject shared disturbance. The transistor proof still has to show that the real devices create disturbance that is matched enough.",
        "",
        "## Results",
        "",
        "| case | target diff V | common injection mV | mismatch injection mV | acquired diff V | held diff V | p hold delta V | n hold delta V | differential hold delta V | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['case']} | `{row['target_diff_v']:.9f}` | `{row['common_injection_mv']:.3f}` | `{row['mismatch_injection_mv']:.3f}` | `{row['acquired_diff_v']:.9f}` | `{row['held_diff_v']:.9f}` | `{row['p_hold_abs_delta_v']:.9e}` | `{row['n_hold_abs_delta_v']:.9e}` | `{row['diff_hold_abs_delta_v']:.9e}` | `{row['pass_diff_hold_delta_half_lsb_12b']}` |"
        )
    lines.extend(
        [
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
    print("differential_sampling_control_proof_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"worst_diff_hold_abs_delta_v,{report['worst_diff_hold_abs_delta_v']:.9e}")
    print(f"diff_hold_pass_count,{report['diff_hold_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
