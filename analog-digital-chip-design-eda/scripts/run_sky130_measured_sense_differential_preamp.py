#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "analog" / "analog-in-memory-foundation-model-hardware"
SPICE_DIR = LAB / "spice"
MEASUREMENTS = LAB / "measurements"
EVIDENCE = ROOT / "evidence" / "aimc-simulator-adapters"
PDK_LIB = Path.home() / "eda-tools" / "pdks" / "sky130A" / "libs.tech" / "ngspice" / "sky130.lib.spice"
SOURCE_RAMP = EVIDENCE / "sky130-frontend-sense-to-transistor-ramp-startup.json"
SOURCE_EXTRACTED_PREAMP = EVIDENCE / "sky130-extracted-frontend-differential-preamp.json"
DECK_OUT = SPICE_DIR / "sky130_measured_sense_differential_preamp.sp"
CSV_OUT = MEASUREMENTS / "sky130-measured-sense-differential-preamp.csv"
OUT_JSON = EVIDENCE / "sky130-measured-sense-differential-preamp.json"
OUT_MD = EVIDENCE / "sky130-measured-sense-differential-preamp.md"
NGSPICE_TIMEOUT_S = 120


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


def build_deck(row: dict[str, Any]) -> str:
    sense_diff_v = float(row["sense_diff_v"])
    sense_p = 0.9 + sense_diff_v / 2.0
    sense_n = 0.9 - sense_diff_v / 2.0
    return f"""* Measured frontend-sense voltage into Sky130 differential preamp.
* This removes the extracted frontend and tests preamp bias directly.

.lib "{PDK_LIB}" tt
.param vdd=1.8
.param rd=100k
.param itail=20u
.param win=8.0
.param lmin=0.15
.options method=gear reltol=1e-3 abstol=1e-14 vntol=1e-7 gmin=1e-12

VDD vdd 0 {{vdd}}
VINP inp 0 PWL(0 0.9 100p 0.9 700p {sense_p:.12f} 2n {sense_p:.12f})
VINN inn 0 PWL(0 0.9 100p 0.9 700p {sense_n:.12f} 2n {sense_n:.12f})
RDP vdd pre_p {{rd}}
RDN vdd pre_n {{rd}}
XPREP pre_p inp tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
XPREN pre_n inn tail 0 sky130_fd_pr__nfet_01v8 W={{win}} L={{lmin}}
ITAIL tail 0 {{itail}}
CPREP pre_p 0 2f
CPREN pre_n 0 2f

.ic v(pre_p)=0.8 v(pre_n)=0.8 v(tail)=0.231
.tran 100p 2n uic
.measure tran pre_p_end_v FIND v(pre_p) AT=2n
.measure tran pre_n_end_v FIND v(pre_n) AT=2n
.measure tran tail_end_v FIND v(tail) AT=2n
.control
set noaskquit
run
.endc
.end
"""


def run_case(row: dict[str, Any]) -> dict[str, Any]:
    DECK_OUT.write_text(build_deck(row), encoding="utf-8")
    expected_sign = 1 if float(row["input_diff_mv"]) > 0 else -1
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
            "reset_mode": row["reset_mode"],
            "input_diff_mv": row["input_diff_mv"],
            "sense_diff_v": row["sense_diff_v"],
            "ngspice_returncode": None,
            "ngspice_timed_out": True,
            "measured": False,
            "sign_preserved": False,
            "output_margin_pass": False,
        }
    out: dict[str, Any] = {
        "reset_mode": row["reset_mode"],
        "input_diff_mv": row["input_diff_mv"],
        "sense_diff_v": row["sense_diff_v"],
        "ngspice_returncode": result.returncode,
        "ngspice_timed_out": False,
        "measured": result.returncode == 0,
    }
    if result.returncode != 0:
        out["error_excerpt"] = (result.stdout + result.stderr)[-1200:]
        out["sign_preserved"] = False
        out["output_margin_pass"] = False
        return out
    pre_p_v = read_measure(result.stdout, "pre_p_end_v")
    pre_n_v = read_measure(result.stdout, "pre_n_end_v")
    preamp_diff_v = pre_n_v - pre_p_v
    measured_sign = 1 if preamp_diff_v > 0 else -1 if preamp_diff_v < 0 else 0
    out.update(
        {
            "pre_p_end_v": pre_p_v,
            "pre_n_end_v": pre_n_v,
            "tail_end_v": read_measure(result.stdout, "tail_end_v"),
            "preamp_output_diff_v": preamp_diff_v,
            "expected_sign": expected_sign,
            "measured_sign": measured_sign,
            "sign_preserved": measured_sign == expected_sign,
            "output_margin_pass": abs(preamp_diff_v) >= 0.0005,
            "sense_to_preamp_gain_v_per_v": preamp_diff_v / float(row["sense_diff_v"]),
        }
    )
    return out


def build_report() -> dict[str, Any]:
    if not PDK_LIB.exists():
        raise FileNotFoundError(PDK_LIB)
    ramp = json.loads(SOURCE_RAMP.read_text(encoding="utf-8"))
    extracted_preamp = json.loads(SOURCE_EXTRACTED_PREAMP.read_text(encoding="utf-8"))
    source_rows = [row for row in ramp["rows"] if row.get("ramp_startup_measured")]
    DECK_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [run_case(row) for row in source_rows]
    measured = [row for row in rows if row["measured"]]
    sign_pass = sum(1 for row in rows if row["sign_preserved"])
    margin_pass = sum(1 for row in rows if row["output_margin_pass"])
    timed_out = sum(1 for row in rows if row["ngspice_timed_out"])
    passed = len(rows) > 0 and len(measured) == len(rows) and sign_pass == len(rows) and margin_pass == len(rows)
    return {
        "result_type": "sky130_measured_sense_differential_preamp",
        "status": "measured_sense_differential_preamp_passed_not_extracted_frontend_or_strict_evidence" if passed else "measured_sense_differential_preamp_failed",
        "source_ramp_startup": rel(SOURCE_RAMP),
        "source_extracted_frontend_differential_preamp": rel(SOURCE_EXTRACTED_PREAMP),
        "generated_deck": rel(DECK_OUT),
        "csv": rel(CSV_OUT),
        "pdk_model_library": str(PDK_LIB),
        "uses_measured_frontend_sense_voltage": True,
        "uses_extracted_frontend_transient": False,
        "uses_sky130_differential_preamp": True,
        "uses_clocked_latch": False,
        "uses_sar_loop": False,
        "case_count": len(rows),
        "measured_case_count": len(measured),
        "timed_out_case_count": timed_out,
        "sign_pass_count": sign_pass,
        "output_margin_pass_count": margin_pass,
        "minimum_abs_preamp_output_diff_v": min((abs(row["preamp_output_diff_v"]) for row in measured), default=0.0),
        "minimum_sense_to_preamp_gain_v_per_v": min((abs(row["sense_to_preamp_gain_v_per_v"]) for row in measured), default=0.0),
        "prior_extracted_preamp_timed_out_case_count": extracted_preamp["timed_out_case_count"],
        "same_run_strict_payload_ready": False,
        "accepted_post_layout_written": False,
        "rows": rows,
        "claim_boundary": {
            "allowed": "tests whether the same differential preamp bias can resolve the measured frontend sense voltages when the extracted frontend is removed",
            "not_allowed": "does not prove extracted frontend loading, latch behavior, SAR conversion, post-layout energy, DRC/LVS, or accepted converter evidence",
        },
    }


def write_csv(report: dict[str, Any]) -> None:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({key for row in report["rows"] for key in row})
    with CSV_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(report["rows"])


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Sky130 Measured Sense Differential Preamp",
        "",
        f"- status: `{report['status']}`",
        f"- uses measured frontend sense voltage: `{report['uses_measured_frontend_sense_voltage']}`",
        f"- uses extracted frontend transient: `{report['uses_extracted_frontend_transient']}`",
        f"- uses Sky130 differential preamp: `{report['uses_sky130_differential_preamp']}`",
        f"- case count: `{report['case_count']}`",
        f"- measured case count: `{report['measured_case_count']}`",
        f"- timed-out case count: `{report['timed_out_case_count']}`",
        f"- sign pass count: `{report['sign_pass_count']}`",
        f"- output margin pass count: `{report['output_margin_pass_count']}`",
        f"- minimum abs preamp output diff V: `{report['minimum_abs_preamp_output_diff_v']:.9e}`",
        f"- minimum sense-to-preamp gain V/V: `{report['minimum_sense_to_preamp_gain_v_per_v']:.6f}`",
        f"- same-run strict payload ready: `{report['same_run_strict_payload_ready']}`",
        f"- accepted post-layout written: `{report['accepted_post_layout_written']}`",
        f"- csv: `{report['csv']}`",
        "",
        "## First Principle",
        "",
        "The failed extracted-frontend preamp run mixed two possible causes: the preamp bias might be wrong, or the extracted frontend might become unstable when attached to the preamp gates. This runner removes the frontend and drives the preamp with the already measured sense voltages.",
        "",
        "If this passes, the preamp can resolve the voltage in principle and the next problem is loading the extracted frontend. If this fails, the preamp bias itself is wrong and should be tuned before reconnecting the frontend.",
        "",
        "## Results",
        "",
        "| reset mode | input diff mV | sense diff uV | preamp output diff mV | gain V/V | sign preserved | margin pass |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        if not row["measured"]:
            lines.append(f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['sense_diff_v'] * 1e6:.6f}` | failed | failed | `False` | `False` |")
            continue
        lines.append(
            f"| `{row['reset_mode']}` | `{row['input_diff_mv']:.6f}` | `{row['sense_diff_v'] * 1e6:.6f}` | `{row['preamp_output_diff_v'] * 1000.0:.6f}` | `{row['sense_to_preamp_gain_v_per_v']:.6f}` | `{row['sign_preserved']}` | `{row['output_margin_pass']}` |"
        )
    lines.extend(["", "## Refused Claim", "", report["claim_boundary"]["not_allowed"], ""])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report = build_report()
    write_csv(report)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report)
    print("sky130_measured_sense_differential_preamp")
    print(f"status,{report['status']}")
    print(f"case_count,{report['case_count']}")
    print(f"measured_case_count,{report['measured_case_count']}")
    print(f"timed_out_case_count,{report['timed_out_case_count']}")
    print(f"sign_pass_count,{report['sign_pass_count']}")
    print(f"output_margin_pass_count,{report['output_margin_pass_count']}")
    print(f"minimum_abs_preamp_output_diff_v,{report['minimum_abs_preamp_output_diff_v']:.9e}")
    print(f"accepted_post_layout_written,{report['accepted_post_layout_written']}")
    print(f"json,{OUT_JSON}")
    print(f"markdown,{OUT_MD}")
    print(f"csv,{CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
