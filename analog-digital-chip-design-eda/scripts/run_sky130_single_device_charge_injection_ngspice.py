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
DECK_OUT = SPICE_DIR / "sky130_single_device_charge_injection.sp"
CSV_OUT = MEASUREMENTS / "sky130-single-device-charge-injection-ngspice.csv"
OUT_JSON = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-single-device-charge-injection-ngspice.json"
OUT_MD = ROOT / "evidence" / "aimc-simulator-adapters" / "sky130-single-device-charge-injection-ngspice.md"
NGSPICE_TIMEOUT_S = 10


@dataclass(frozen=True)
class Case:
    name: str
    input_v: float
    wn_um: float
    csample_p: float


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
    return f"""* Sky130 single-device charge injection fixture.
* One nfet samples a DC input onto a capacitor; the gate edge then disturbs the held node.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param lmin=0.15
.param wn={case.wn_um}
.param csample={case.csample_p}p
.param vin={case.input_v}

VDD vdd 0 {{vdd}}
VSS vss 0 0
VIN in 0 PULSE(0 {{vin}} 0.1n 20p 20p 20n 40n)
VG ctrl 0 PULSE(0 {{vdd}} 0.2n 20p 20p 7n 20n)
XEDGE in ctrl hold vss sky130_fd_pr__nfet_01v8 W={{wn}} L={{lmin}}
CSAMPLE hold 0 {{csample}}
RLEAK hold 0 100G

.tran 2p 10n
.measure tran before_edge_v FIND v(hold) AT=6.8n
.measure tran after_edge_v FIND v(hold) AT=8.5n
.measure tran input_v FIND v(in) AT=6.8n
.control
run
.endc

.end
"""


def run_case(case: Case) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(case), encoding="utf-8")
    half_lsb = 1.8 / 4096.0 / 2.0
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
            "input_v": case.input_v,
            "wn_um": case.wn_um,
            "csample_p": case.csample_p,
            "ngspice_timed_out": True,
            "ngspice_returncode": None,
            "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
            "half_lsb_12b_v": half_lsb,
            "pass_half_lsb_12b": False,
        }
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    before = read_measure(result.stdout, "before_edge_v")
    after = read_measure(result.stdout, "after_edge_v")
    measured_input = read_measure(result.stdout, "input_v")
    delta = after - before
    return {
        "case": case.name,
        "input_v": case.input_v,
        "measured_input_v": measured_input,
        "wn_um": case.wn_um,
        "csample_p": case.csample_p,
        "before_edge_v": before,
        "after_edge_v": after,
        "edge_delta_v": delta,
        "edge_abs_delta_v": abs(delta),
        "sample_error_before_edge_v": abs(measured_input - before),
        "inferred_charge_c": abs(delta) * case.csample_p * 1e-12,
        "half_lsb_12b_v": half_lsb,
        "pass_half_lsb_12b": abs(delta) <= half_lsb,
        "ngspice_timed_out": False,
        "ngspice_returncode": result.returncode,
        "ngspice_timeout_s": NGSPICE_TIMEOUT_S,
    }


def fmt(value: float | None) -> str:
    return "not measured" if value is None else f"{value:.9e}"


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    cases = [
        Case("mid_0p2p_1x", 0.9, 1.0, 0.2),
        Case("mid_1p0p_1x", 0.9, 1.0, 1.0),
        Case("mid_1p0p_2x", 0.9, 2.0, 1.0),
    ]
    rows = [run_case(case) for case in cases]
    measured = [row for row in rows if not row["ngspice_timed_out"]]
    return {
        "result_type": "sky130_single_device_charge_injection_ngspice",
        "status": "sky130_single_device_charge_injection_characterized_not_converter_proof",
        "topology": "single_sky130_nfet_sample_path_to_hold_capacitor",
        "pdk_model_library": str(PDK_LIB),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "device_models": ["sky130_fd_pr__nfet_01v8"],
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": sum(1 for row in rows if row["ngspice_timed_out"]),
        "rows": rows,
        "half_lsb_12b_v": 1.8 / 4096.0 / 2.0,
        "worst_edge_abs_delta_v": max((row.get("edge_abs_delta_v", 0) for row in measured), default=None),
        "pass_count": sum(1 for row in rows if row["pass_half_lsb_12b"]),
        "candidate_post_layout_written": False,
        "accepted_post_layout_written": False,
        "claim_boundary": {
            "allowed": "characterizes voltage movement on a held capacitor after one Sky130 nfet sampling path turns off",
            "not_allowed": "does not prove a complete sampling switch, differential matching, comparator behavior, SAR conversion, extracted layout, DRC/LVS signoff, or accepted replacement economics",
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
        "# Sky130 Single-Device Charge Injection Ngspice",
        "",
        f"- status: `{report['status']}`",
        f"- topology: `{report['topology']}`",
        f"- PDK model library: `{report['pdk_model_library']}`",
        f"- generated deck: `{report['generated_deck']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed out case count: `{report['timed_out_case_count']}`",
        f"- half LSB 12b V: `{report['half_lsb_12b_v']:.9e}`",
        f"- worst edge abs delta V: `{fmt(report['worst_edge_abs_delta_v'])}`",
        f"- pass count: `{report['pass_count']}` of `{report['case_count']}`",
        f"- candidate post-layout written: `{report['candidate_post_layout_written']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "A MOS gate is separated from the held node by capacitance. When the gate voltage moves, some charge is pushed through that capacitance. The held node is a capacitor, so the pushed charge becomes a voltage step.",
        "",
        "This fixture keeps the signal path but makes it as small as possible. One Sky130 nfet connects a DC input to the hold capacitor. The gate then falls from high to low. The measured voltage step after turn-off is the smallest normal-switch unit behind clock feedthrough and charge injection.",
        "",
        "This is not a sample-and-hold proof. It is a device-level measurement that tells us whether the next differential or bootstrapped switch deck is working from a measured disturbance size instead of a guess.",
        "",
        "## Results",
        "",
        "| case | input V | Wn um | Csample pF | before edge V | after edge V | edge delta V | sample error before edge V | inferred charge C | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report["rows"]:
        if row["ngspice_timed_out"]:
            lines.append(f"| {row['case']} | `{row['input_v']:.9f}` | `{row['wn_um']:.3f}` | `{row['csample_p']:.3f}` | timeout | timeout | timeout | timeout | timeout | `False` |")
            continue
        lines.append(
            f"| {row['case']} | `{row['measured_input_v']:.9f}` | `{row['wn_um']:.3f}` | `{row['csample_p']:.3f}` | `{row['before_edge_v']:.9f}` | `{row['after_edge_v']:.9f}` | `{row['edge_delta_v']:.9e}` | `{row['sample_error_before_edge_v']:.9e}` | `{row['inferred_charge_c']:.9e}` | `{row['pass_half_lsb_12b']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report["rows"])
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_single_device_charge_injection_ngspice")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"worst_edge_abs_delta_v,{fmt(report['worst_edge_abs_delta_v'])}")
    print(f"pass_count,{report['pass_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
