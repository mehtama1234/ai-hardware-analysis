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
DECK_OUT = SPICE_DIR / "sky130_bootstrapped_switch.sp"
CSV_OUT = MEASUREMENTS / "sky130-bootstrapped-switch-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bootstrapped-switch-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-bootstrapped-switch-ngspice.md"
NGSPICE_TIMEOUT_S = 10


@dataclass(frozen=True)
class Case:
    name: str
    input_v: float


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


def read_measure(stdout: str, name: str) -> float:
    values: list[float] = []
    for raw in stdout.splitlines():
        match = re.search(rf"{re.escape(name)}\s+=\s+([-+0-9.eE]+)", raw)
        if match:
            values.append(float(match.group(1)))
    if not values:
        raise ValueError(f"expected ngspice measurement {name!r}, found none")
    return values[-1]


def build_deck(case: Case) -> str:
    return f"""* Sky130 idealized bootstrapped-switch fixture.
* The nfet gate is driven near input + vdd during sample, then pulled to zero during hold.

.lib "{PDK_LIB}" tt
.param vin={case.input_v}
.param vdd=1.8
.param lmin=0.15
.param wn=2.0
.param csample=0.2p
.param cload=0.05p

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VBOOT boot 0 PULSE(0 {{vin+vdd}} 0.2n 20p 20p 7n 20n)

XSW in boot sample vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
CSAMPLE sample 0 {{csample}}
CLOAD sample 0 {{cload}}
RLEAK sample 0 100G

.tran 5p 10n
.measure tran acquired_v FIND v(sample) AT=6.8n
.measure tran held_v FIND v(sample) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.measure tran boot_v FIND v(boot) AT=6.8n
.measure tran acquisition_abs_error_v PARAM='abs(input_v-acquired_v)'
.measure tran hold_abs_delta_v PARAM='abs(held_v-acquired_v)'
.measure tran total_abs_error_v PARAM='abs(input_v-held_v)'
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb_12b_v = 1.8 / 4096.0 / 2.0
    try:
        result = subprocess.run(
            ["ngspice", "-b", str(DECK_OUT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=NGSPICE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return {
            "case": case.name,
            "target_input_v": case.input_v,
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "half_lsb_12b_v": half_lsb_12b_v,
            "pass_acquisition_half_lsb_12b": False,
            "pass_hold_delta_half_lsb_12b": False,
            "pass_total_error_half_lsb_12b": False,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    acquired_v = read_measure(result.stdout, "acquired_v")
    held_v = read_measure(result.stdout, "held_v")
    input_v = read_measure(result.stdout, "input_v")
    boot_v = read_measure(result.stdout, "boot_v")
    acquisition_error = abs(input_v - acquired_v)
    hold_delta = abs(held_v - acquired_v)
    total_error = abs(input_v - held_v)
    return {
        "case": case.name,
        "target_input_v": case.input_v,
        "measured_input_v": input_v,
        "boot_v": boot_v,
        "acquired_v": acquired_v,
        "held_v": held_v,
        "acquisition_abs_error_v": acquisition_error,
        "hold_abs_delta_v": hold_delta,
        "total_abs_error_v": total_error,
        "half_lsb_12b_v": half_lsb_12b_v,
        "pass_acquisition_half_lsb_12b": acquisition_error <= half_lsb_12b_v,
        "pass_hold_delta_half_lsb_12b": hold_delta <= half_lsb_12b_v,
        "pass_total_error_half_lsb_12b": total_error <= half_lsb_12b_v,
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    rows = [run_case(case) for case in [Case("low_bootstrap", 0.3), Case("mid_bootstrap", 0.9), Case("high_bootstrap", 1.5)]]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    return {
        "result_type": "sky130_bootstrapped_switch_ngspice",
        "status": "sky130_bootstrapped_switch_characterized_not_converter_proof",
        "topology": "idealized_input_referenced_bootstrapped_nfet_sample_switch",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
        "rows": rows,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_acquisition_abs_error_v": max((row.get("acquisition_abs_error_v", 0) for row in measured), default=None),
        "worst_hold_abs_delta_v": max((row.get("hold_abs_delta_v", 0) for row in measured), default=None),
        "worst_total_abs_error_v": max((row.get("total_abs_error_v", 0) for row in measured), default=None),
        "acquisition_pass_count": sum(1 for row in rows if row["pass_acquisition_half_lsb_12b"]),
        "hold_delta_pass_count": sum(1 for row in rows if row["pass_hold_delta_half_lsb_12b"]),
        "total_error_pass_count": sum(1 for row in rows if row["pass_total_error_half_lsb_12b"]),
        "idealized_bootstrap_driver": True,
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "characterizes an idealized input-referenced bootstrapped Sky130 nfet sample switch over low, mid, and high input",
            "not_allowed": "does not prove a real bootstrap charge pump, reliability-safe gate voltage, comparator decision, SAR conversion, mismatch, noise, extracted transistor layout, DRC/LVS signoff, or accepted replacement economics",
        },
    }


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def write_csv(rows: list[dict[str, Any]]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        keys = sorted({key for row in rows for key in row})
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Bootstrapped Switch Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- idealized bootstrap driver: `{report['idealized_bootstrap_driver']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst acquisition abs error V: `{fmt(report['worst_acquisition_abs_error_v'])}`",
        f"- worst hold abs delta V: `{fmt(report['worst_hold_abs_delta_v'])}`",
        f"- worst total abs error V: `{fmt(report['worst_total_abs_error_v'])}`",
        f"- acquisition pass count: `{report['acquisition_pass_count']}` of `{report['case_count']}`",
        f"- hold delta pass count: `{report['hold_delta_pass_count']}` of `{report['case_count']}`",
        f"- total error pass count: `{report['total_error_pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A plain switch gets weaker when the input voltage moves closer to the fixed gate voltage. A bootstrapped switch attacks that by moving the gate with the input. The switch then sees a more constant gate-to-source voltage while sampling.",
        "",
        "This fixture tests that idea in the simplest measurable way. The nfet switch is a Sky130 device, but the bootstrap driver is idealized. During sampling, the gate is driven near input plus supply. During hold, the gate is pulled back to zero. That is enough to ask whether constant overdrive helps the sample-and-hold problem before building a real bootstrap driver.",
        "",
        "This is not a finished circuit. A real bootstrap needs devices that charge, hold, and discharge the gate safely. It must also respect oxide limits. This run is only a topology test.",
        "",
        "## Results",
        "",
        "| case | input V | boot V | acquired V | held V | acquisition error V | hold delta V | total error V |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| {row['case']} | `{row['target_input_v']:.9f}` | timeout | timeout | timeout | timeout | timeout | timeout |")
            continue
        lines.append(
            f"| {row['case']} | `{row['measured_input_v']:.9f}` | `{row['boot_v']:.9f}` | `{row['acquired_v']:.9f}` | `{row['held_v']:.9f}` | `{row['acquisition_abs_error_v']:.9e}` | `{row['hold_abs_delta_v']:.9e}` | `{row['total_abs_error_v']:.9e}` |"
        )
    lines.extend(
        [
            "",
            "## Reading The Result",
            "",
            "If acquisition improves but hold still fails, the switch has solved only the charging part. If hold improves too, the next task is to replace the idealized gate drive with a real bootstrap circuit and rerun the same low, mid, and high input checks.",
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
    print("sky130_bootstrapped_switch_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"worst_acquisition_abs_error_v,{fmt(report['worst_acquisition_abs_error_v'])}")
    print(f"worst_hold_abs_delta_v,{fmt(report['worst_hold_abs_delta_v'])}")
    print(f"worst_total_abs_error_v,{fmt(report['worst_total_abs_error_v'])}")
    print(f"hold_delta_pass_count,{report['hold_delta_pass_count']}")
    print(f"total_error_pass_count,{report['total_error_pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
